import json
import os
from datetime import datetime

class StateController:
    def __init__(self, state_dir='runtime/state'):
        self.state_dir = os.path.abspath(state_dir)
        self.tasks_file = os.path.join(self.state_dir, 'tasks.json')
        self.workers_file = os.path.join(self.state_dir, 'workers.json')
        self.events_file = os.path.join(self.state_dir, 'events.ndjson')
        self.pulse_file = os.path.join(self.state_dir, 'pulse.json')

        os.makedirs(self.state_dir, exist_ok=True)

        self.tasks = self._load_json(self.tasks_file, default={})
        self.workers = self._load_json(self.workers_file, default={})
        self.pulse = self._load_json(self.pulse_file, default={})

        self.task_transitions = {
            'proposed': ['backlog'],
            'backlog': ['active'],
            'active': ['delivered'],
            'delivered': ['accepted', 'blocked'],
            'accepted': [],
            'blocked': ['backlog']
        }

        self.worker_transitions = {
            'spawned': ['linked'],
            'linked': ['executing', 'failure', 'timeout'],
            'executing': ['verifying', 'failure', 'timeout'],
            'verifying': ['terminated'],
            'failure': ['terminated'],
            'timeout': ['terminated'],
            'terminated': []
        }

    def _load_json(self, filepath, default):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return default
        return default

    def _save_json(self, filepath, data):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

    def _append_event(self, event):
        try:
            cwd = os.getcwd()
            abs_path = os.path.abspath(self.events_file)
            parent_dir = os.path.dirname(abs_path)

            print(f"[StateController] CWD: {cwd}")
            print(f"[StateController] Events file abs path: {abs_path}")

            if not os.path.exists(parent_dir):
                print(f"[StateController] Parent dir missing, creating: {parent_dir}")
                os.makedirs(parent_dir, exist_ok=True)

            event_json = json.dumps(event)
            print(f"[StateController] event object: {repr(event)}")
            print(f"[StateController] serialized event JSON: {repr(event_json)}")
            print(f"[StateController] event JSON length: {len(event_json)}")

            if not event_json:
                raise ValueError("Empty event serialization")

            with open(abs_path, 'a', encoding='utf-8') as f:
                print(f"[StateController] Opening events file for append: {abs_path}")
                f.write(event_json + '\n')
                print("[StateController] Write complete")
                f.flush()
                print("[StateController] Flush complete")
                os.fsync(f.fileno())
                print("[StateController] Fsync complete")

            with open(abs_path, 'r', encoding='utf-8') as f:
                contents = f.read()
                print(f"[StateController] Events file size after write: {len(contents)}")
                last_lines = [line for line in contents.splitlines()[-10:] if line.strip()]
                print("[StateController] Last 10 events:")
                for line in last_lines:
                    print(line)

            print("[StateController] Searching for all events.ndjson files in workspace:")
            for root, dirs, files in os.walk('.'):  # assume cwd is workspace root
                for file in files:
                    if file == 'events.ndjson':
                        found_path = os.path.join(root, file)
                        print(f"- Found: {os.path.abspath(found_path)}")

        except Exception as e:
            print(f"[StateController] Event write failure: {e}")
            raise

    def _now(self):
        return datetime.utcnow().isoformat()

    def _validate_task_transition(self, current_state, next_state):
        return next_state in self.task_transitions.get(current_state, [])

    def _validate_worker_transition(self, current_state, next_state):
        return next_state in self.worker_transitions.get(current_state, [])

    def create_task(self, task_id, owner=None, details=None):
        print(f"[StateController] create_task entered for task_id={task_id} with owner={owner}")

        if task_id in self.tasks:
            raise ValueError(f"Task {task_id} already exists.")

        if details is None:
            details = {}

        if owner is not None:
            details = dict(details)
            details["owner"] = owner

        print(f"[StateController] Tasks file path: {os.path.abspath(self.tasks_file)}")
        print(f"[StateController] Workers file path: {os.path.abspath(self.workers_file)}")

        self.tasks[task_id] = {
            "state": "proposed",
            "details": details,
            "worker_id": None,
        }

        print(f"[StateController] Saving tasks.json...")
        self._save_json(self.tasks_file, self.tasks)
        print(f"[StateController] Saving tasks.json complete")

        event = {
            "event": "TASK_CREATED",
            "task_id": task_id,
            "details": details,
            "timestamp": self._now(),
        }

        print(f"[StateController] Appending TASK_CREATED event")
        self._append_event(event)

    def activate_task(self, task_id):
        print(f"[StateController] activate_task entered for {task_id}")

        current_state = self.tasks.get(task_id, {}).get("state")

        if current_state == "active":
            return
        elif current_state != "backlog":
            raise ValueError(f"Illegal task activation from state: {current_state}")

        self._change_task_state(task_id, "active")

    def enqueue_task(self, task_id):
        print(f"[StateController] enqueue_task entered for {task_id}")

        current_state = self.tasks.get(task_id, {}).get("state")

        if current_state != "proposed":
            raise ValueError(f"Illegal task enqueue from state: {current_state}")

        self._change_task_state(task_id, "backlog")

    def link_worker(self, task_id, worker_id):
        print(f"[StateController] link_worker entered with task_id={task_id} worker_id={worker_id}")

        if worker_id in self.workers:
            raise ValueError(f"Worker {worker_id} already registered.")

        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} does not exist.")

        print(f"[StateController] Current task record before mutation: {self.tasks[task_id]}")
        print(f"[StateController] Workers dict before mutation: {self.workers.keys()}")

        self.workers[worker_id] = {
            "task_id": task_id,
            "state": "linked",
        }

        print(f"[StateController] Workers dict after assignment: {self.workers[worker_id]}")

        self.tasks[task_id]["worker_id"] = worker_id

        print(f"[StateController] Task record after assignment: {self.tasks[task_id]}")

        print(f"[StateController] Saving workers.json...")
        self._save_json(self.workers_file, self.workers)
        print(f"[StateController] Saved workers.json")

        print(f"[StateController] Saving tasks.json...")
        self._save_json(self.tasks_file, self.tasks)
        print(f"[StateController] Saved tasks.json")

        print(f"[StateController] Appending WORKER_LINKED event")
        self._append_event({
            "event": "WORKER_LINKED",
            "worker_id": worker_id,
            "task_id": task_id,
            "timestamp": self._now(),
        })
        print(f"[StateController] Appended WORKER_LINKED event")

    def start_worker_execution(self, worker_id):
        print(f"[StateController] start_worker_execution entered for {worker_id}")
        print(f"[StateController] Worker current state before change: {self.workers.get(worker_id)}")
        print(f"[StateController] Calling _change_worker_state with executing")
        self._change_worker_state(worker_id, "executing")
        print(f"[StateController] Worker state after change: {self.workers.get(worker_id)}")

        with open(self.workers_file, 'r', encoding='utf-8') as f:
            workers_data = json.load(f)
            print(f"[StateController] Workers.json after start_worker_execution:")
            print(workers_data.get(worker_id))

        with open(self.events_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"[StateController] Last 10 events after start_worker_execution:")
            for line in lines[-10:]:
                print(line.strip())

    def record_worker_done(self, worker_id):
        print(f"[StateController] record_worker_done entered for {worker_id}")

        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found.")

        self._change_worker_state(worker_id, "verifying")

        self._append_event({
            "event": "WORKER_DONE",
            "worker_id": worker_id,
            "task_id": self.workers[worker_id]["task_id"],
            "timestamp": self._now(),
        })

        self._save_json(self.workers_file, self.workers)

    def record_task_delivered(self, task_id):
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found.")

        current_state = self.tasks[task_id]["state"]
        if current_state != "active":
            raise ValueError(f"Illegal task state transition: {current_state} -> delivered")

        self._change_task_state(task_id, "delivered")

        self._append_event({
            "event": "TASK_DELIVERED",
            "task_id": task_id,
            "timestamp": self._now(),
        })

    def record_worker_blocked(self, worker_id, reason="blocked"):
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found.")

        task_id = self.workers[worker_id]["task_id"]  # Task enters blocked, worker exits through failure path
        if self.tasks[task_id]["state"] != "blocked":
            self._change_task_state(task_id, "blocked")

        if self.workers[worker_id]["state"] == "executing":
            self._change_worker_state(worker_id, "failure")

        self._append_event({
            "event": "WORKER_BLOCKED",
            "worker_id": worker_id,
            "task_id": task_id,
            "reason": reason,
            "timestamp": self._now(),
        })

    def record_worker_timeout(self, worker_id):
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found.")

        self._change_worker_state(worker_id, "timeout")

        self._append_event({
            "event": "WORKER_TIMEOUT",
            "worker_id": worker_id,
            "task_id": self.workers[worker_id]["task_id"],
            "timestamp": self._now(),
        })

    def record_worker_failure(self, worker_id, reason="failure"):
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found.")

        self._change_worker_state(worker_id, "failure")

        self._append_event({
            "event": "WORKER_FAILURE",
            "worker_id": worker_id,
            "task_id": self.workers[worker_id]["task_id"],
            "reason": reason,
            "timestamp": self._now(),
        })

    def verify_task(self, task_id):
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found.")

        self._append_event({
            "event": "TASK_VERIFIED",
            "task_id": task_id,
            "timestamp": self._now(),
        })

    def accept_task(self, task_id):
        current_state = self.tasks.get(task_id, {}).get("state")
        if current_state != "delivered":
            raise ValueError(f"Illegal task state transition: {current_state} -> accepted")

        self._change_task_state(task_id, "accepted")

        self._append_event({
            "event": "TASK_ACCEPTED",
            "task_id": task_id,
            "timestamp": self._now(),
        })

    def block_task(self, task_id):
        current_state = self.tasks.get(task_id, {}).get("state")
        if current_state != "delivered":
            raise ValueError(f"Illegal task state transition: {current_state} -> blocked")

        self._change_task_state(task_id, "blocked")

    def terminate_worker(self, worker_id):
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found.")

        current_state = self.workers[worker_id]["state"]
        if current_state != "terminated":
            self._change_worker_state(worker_id, "terminated")

        task_id = self.workers[worker_id]["task_id"]
        self.tasks[task_id]["worker_id"] = None

        self._save_json(self.workers_file, self.workers)
        self._save_json(self.tasks_file, self.tasks)

        self._append_event({
            "event": "WORKER_TERMINATED",
            "worker_id": worker_id,
            "task_id": task_id,
            "timestamp": self._now(),
        })

    # ---------------------------------------------------------------------
    # state transition helpers
    # ---------------------------------------------------------------------

    def _change_task_state(self, task_id, next_state):
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found.")

        current_state = self.tasks[task_id]["state"]
        if not self._validate_task_transition(current_state, next_state):
            raise ValueError(f"Illegal task state transition: {current_state} -> {next_state}")

        self.tasks[task_id]["state"] = next_state
        self._save_json(self.tasks_file, self.tasks)

        self._append_event({
            "event": "TASK_STATE_CHANGED",
            "task_id": task_id,
            "old_state": current_state,
            "new_state": next_state,
            "timestamp": self._now(),
        })

    def _change_worker_state(self, worker_id, next_state):
        if worker_id not in self.workers:
            raise ValueError(f"Worker {worker_id} not found.")

        current_state = self.workers[worker_id]["state"]
        if not self._validate_worker_transition(current_state, next_state):
            raise ValueError(f"Illegal worker state transition: {current_state} -> {next_state}")

        self.workers[worker_id]["state"] = next_state
        self._save_json(self.workers_file, self.workers)

        self._append_event({
            "event": "WORKER_STATE_CHANGED",
            "worker_id": worker_id,
            "old_state": current_state,
            "new_state": next_state,
            "timestamp": datetime.utcnow().isoformat(),
        })