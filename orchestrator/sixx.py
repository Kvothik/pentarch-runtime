import runtime.state_controller as state_controller
import workers.forge as forge_worker
import workers.atlas as atlas_worker
import workers.aegis as aegis_worker
import workers.sentinel as sentinel_worker
import time
import os
import json

class SixxOrchestrator:
    def __init__(self):
        self.state_ctrl = state_controller.StateController()
        self.worker_modules = {
            'owner:backend': forge_worker,
            'owner:mobile': atlas_worker,
            'owner:architecture': aegis_worker,
            'owner:qa': sentinel_worker
        }
        self.events_file = self.state_ctrl.events_file
        self.offset_file = os.path.join(os.path.dirname(self.events_file), 'events.offset')
        self.last_offset = 0
        self.load_last_offset()
        self._event_remainder = ""

    def load_last_offset(self):
        try:
            with open(self.offset_file, 'r') as f:
                self.last_offset = int(f.read().strip())
        except Exception:
            self.last_offset = 0

    def save_last_offset(self, offset):
        temp_path = self.offset_file + '.tmp'
        with open(temp_path, 'w') as f:
            f.write(str(offset))
        os.replace(temp_path, self.offset_file)
        self.last_offset = offset

    def read_new_events(self):
        events = []
        try:
            print(f"[Sixx] Current offset before read: {self.last_offset}")
            if not os.path.exists(self.offset_file):
                self.last_offset = 0
            file_size = os.path.getsize(self.events_file) if os.path.exists(self.events_file) else 0
            print(f"[Sixx] File size before read: {file_size}")
            if self.last_offset > file_size:
                self.last_offset = 0
                print(f"[Sixx] Offset reset to 0 because last_offset > file_size")
            bytes_read = 0
            raw_data = ''
            with open(self.events_file, 'r', encoding='utf-8') as f:
                f.seek(self.last_offset)
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    raw_data += chunk
                    if len(raw_data) > 200:
                        print(f"[Sixx] Raw data chunk read (truncated): {repr(raw_data[:200])}... (truncated)")
                    else:
                        print(f"[Sixx] Raw data chunk read: {repr(raw_data)}")
            lines = raw_data.split('\n')
            if raw_data and not raw_data.endswith('\n'):
                remainder = lines.pop()
                print(f"[Sixx] Partial last line detected (length {len(remainder)}), saving to remainder buffer")
                self._event_remainder = remainder
            else:
                self._event_remainder = ''
            line_count = 0
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    events.append(event)
                    print(f"[Sixx] Parsed event type: {event.get('event') or event.get('type')}")
                    line_count += 1
                except json.JSONDecodeError:
                    print(f"[Sixx] Skipping malformed line: {line}")
            print(f"[Sixx] Number of lines parsed this read: {line_count}")
            if line_count > 0:
                old_offset = self.last_offset
                new_offset = self.last_offset + bytes_read
                self.save_last_offset(new_offset)
                print(f"[Sixx] Offset advanced from {old_offset} to {new_offset}")
            else:
                print(f"[Sixx] No complete lines parsed, offset not advanced")
            print(f"[Sixx] Total events parsed this cycle: {len(events)}")
        except FileNotFoundError:
            print(f"[Sixx] events.ndjson or offset file not found")
            return []
        return events

    def handle_event(self, event):
        etype = event.get('event') or event.get('type')
        print(f"[Sixx] Handling event type: {etype}")
        handlers = {
            'TASK_STATE_CHANGED': self.handle_task_state_changed,
            'WORKER_DONE': self.handle_worker_done,
            'TASK_VERIFIED': self.handle_task_verified,
            'WORKER_BLOCKED': self.handle_worker_blocked,
            'WORKER_TIMEOUT': self.handle_worker_timeout,
            'WORKER_TERMINATED': self.handle_worker_terminated
        }
        handler = handlers.get(etype)
        if handler:
            print(f"[Sixx] Dispatching to handler: {etype}")
            try:
                handler(event)
                print(f"[Sixx] Handler {etype} returned successfully")
            except Exception as e:
                print(f"[Sixx] Handler {etype} raised exception: {e}")
        else:
            print(f"[Sixx] Unknown event type: {etype}")

    def handle_task_state_changed(self, event):
        task_id = event["task_id"]
        new_state = event.get("new_state") or event.get("to_state")
        print("DISPATCHING" if new_state == "backlog" else "NO DISPATCH", task_id, new_state)
        if new_state == "backlog":
            self.dispatch(task_id)

    def handle_worker_done(self, event):
        worker_id = event.get('worker_id')
        print(f"[Sixx] WORKER_DONE event parsed for worker: {worker_id}")
        print(f"[Sixx] Invoking handle_worker_done handler for worker: {worker_id}")
        self.state_ctrl.record_worker_done(worker_id)
        task_id = self.state_ctrl.workers[worker_id]['task_id']
        self.state_ctrl.record_task_delivered(task_id)
        self.state_ctrl.verify_task(task_id)

    def handle_task_verified(self, event):
        task_id = event.get('task_id')
        print(f"[Sixx] TASK_VERIFIED event parsed for task: {task_id}")
        try:
            self.state_ctrl.accept_task(task_id)
            print(f"[Sixx] Task accepted: {task_id}")
        except Exception as e:
            print(f"[Sixx] Could not accept task {task_id}: {e}")

    def handle_worker_blocked(self, event):
        worker_id = event.get('worker_id')
        print(f"[Sixx] WORKER_BLOCKED event parsed from worker: {worker_id}")
        self.state_ctrl.record_worker_blocked(worker_id, event.get('reason', ''))

    def handle_worker_timeout(self, event):
        worker_id = event.get('worker_id')
        print(f"[Sixx] WORKER_TIMEOUT event parsed from worker: {worker_id}")
        self.state_ctrl.record_worker_timeout(worker_id)
        task_id = self.state_ctrl.workers[worker_id]['task_id']
        self.state_ctrl.block_task(task_id)

    def handle_worker_terminated(self, event):
        worker_id = event.get('worker_id')
        print(f"[Sixx] WORKER_TERMINATED event parsed from worker: {worker_id}")
        self.state_ctrl.terminate_worker(worker_id)

    def dispatch(self, task_id):
        print(f"[Sixx] Entering dispatch with task_id: {task_id}")
        task_info = self.state_ctrl.tasks[task_id]
        print(f"[Sixx] Loaded task_info: {task_info}")
        owner_label = task_info['details'].get('owner_label')
        worker_module = self.worker_modules.get(owner_label)
        if not worker_module:
            print(f"[Sixx] No worker module for owner: {owner_label}, cannot dispatch {task_id}")
            return None, None
        worker_id = f"{owner_label}-worker-{task_id}"
        try:
            print(f"[Sixx] Calling link_worker with worker_id {worker_id}")
            self.state_ctrl.link_worker(task_id, worker_id)
            print(f"[Sixx] link_worker succeeded")
        except Exception as e:
            print(f"[Sixx] link_worker raised exception: {e}")
            return None, None
        try:
            print(f"[Sixx] Calling start_worker_execution with worker_id {worker_id}")
            self.state_ctrl.start_worker_execution(worker_id)
            print(f"[Sixx] start_worker_execution succeeded")
        except Exception as e:
            print(f"[Sixx] start_worker_execution raised exception: {e}")
            return None, None
        print(f"[Sixx] Dispatched worker {worker_id} for task {task_id}")
        result = worker_module.execute(task_id)
        return worker_id, worker_module

    def run(self):
        while True:
            events = self.read_new_events()
            if events:
                for event in events:
                    self.handle_event(event)
            else:
                time.sleep(5)


if __name__ == '__main__':
    sixx = SixxOrchestrator()
    sixx.run()
