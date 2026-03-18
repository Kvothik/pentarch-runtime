import json
import os
from threading import Lock

EVENT_FILE = "runtime/state/events.ndjson"
BOARD_VIEW_FILE = "runtime/state/board_view.json"

lock = Lock()

# Maps event states to board columns
STATE_TO_COLUMN = {
    "backlog": "backlog",
    "active": "active",
    "verifying": "verifying",
    "accepted": "accepted",
    "failed": "failed"
}

class BoardProjector:

    def __init__(self):
        self.tasks = {}

    def update_from_event(self, event):
        task_id = event.get("task_id") or event.get("details", {}).get("task_id")
        if not task_id:
            return

        event_type = event.get("event")

        # Handle task state changes
        if event_type == "TASK_STATE_CHANGED":
            new_state = event.get("new_state")
            if new_state:
                self.tasks[task_id] = self.tasks.get(task_id, {})
                self.tasks[task_id]["state"] = new_state

        # Handle worker state changes
        elif event_type == "WORKER_DONE":
            self.tasks[task_id] = self.tasks.get(task_id, {})
            self.tasks[task_id]["state"] = "verifying"

        elif event_type == "TASK_ACCEPTED":
            self.tasks[task_id] = self.tasks.get(task_id, {})
            self.tasks[task_id]["state"] = "accepted"

        elif event_type == "WORKER_FAILURE":
            self.tasks[task_id] = self.tasks.get(task_id, {})
            self.tasks[task_id]["state"] = "failed"

        elif event_type == "TASK_BLOCKED":
            self.tasks[task_id] = self.tasks.get(task_id, {})
            self.tasks[task_id]["state"] = "failed"

        # Persist board view after updates
        self.persist_board_view()

    def persist_board_view(self):
        with lock:
            board_data = {"tasks": self.tasks}
            os.makedirs(os.path.dirname(BOARD_VIEW_FILE), exist_ok=True)
            with open(BOARD_VIEW_FILE, "w") as f:
                json.dump(board_data, f, indent=2)


PROJECTOR = BoardProjector()


def on_new_event(event):
    PROJECTOR.update_from_event(event)


def rebuild_board():
    try:
        with open(EVENT_FILE, "r") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    on_new_event(event)
    except FileNotFoundError:
        pass
    PROJECTOR.persist_board_view()


if __name__ == '__main__':
    import time
    import json

    print("Starting board projector event watch...")
    last_pos = 0

    # Build initial state
    rebuild_board()

    while True:
        try:
            with open(EVENT_FILE, "r") as f:
                f.seek(last_pos)
                new_lines = f.readlines()
                last_pos = f.tell()

            for line in new_lines:
                if line.strip():
                    event = json.loads(line)
                    print(f"Processing event: {event.get('event')} for task {event.get('task_id')}")
                    on_new_event(event)

        except FileNotFoundError:
            # Events file not created yet
            pass

        time.sleep(3)
