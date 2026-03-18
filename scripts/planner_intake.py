import json
import os
import sys
sys.path.insert(0, "/Users/sixx/.openclaw/workspace")
from runtime.state_controller import StateController

PLANNER_TASKS_PATH = "/Users/sixx/.openclaw/workspace/planner/planner_tasks.json"


def intake_task(planner_task_json):
    task = json.loads(planner_task_json)
    
    # Save to planner tasks archive
    os.makedirs(os.path.dirname(PLANNER_TASKS_PATH), exist_ok=True)
    if os.path.exists(PLANNER_TASKS_PATH):
        with open(PLANNER_TASKS_PATH, 'r') as f:
            tasks = json.load(f)
    else:
        tasks = []
    tasks.append(task)
    with open(PLANNER_TASKS_PATH, 'w') as f:
        json.dump(tasks, f, indent=2)

    # Convert to runtime task
    sc = StateController()
    task_id = task.get('title').replace(' ', '-').lower()
    owner = task.get('owner')
    details = task.copy()
    details.pop('title', None)
    details.pop('owner', None)

    print(f"[Planner Intake] Creating task {task_id} for owner {owner}")
    sc.create_task(task_id, owner=owner, details=details)
    sc.enqueue_task(task_id)

    print(f"[Planner Intake] Task {task_id} enqueued")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: planner_intake.py <planner_task_json_file>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        planner_task_json = f.read()
    intake_task(planner_task_json)
