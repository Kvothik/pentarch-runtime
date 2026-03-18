import sys
sys.path.insert(0, "/Users/sixx/.openclaw/workspace")

from runtime.state_controller import StateController

if __name__ == '__main__':
    sc = StateController()
    test_task_id = 'phase4-event-test-1'
    print(f'Creating task {test_task_id}')
    sc.create_task(test_task_id, owner='backend')
    print(f'Enqueuing task {test_task_id}')
    sc.enqueue_task(test_task_id)

    import json
    print('Current tasks.json:')
    with open(sc.tasks_file, 'r') as f:
        print(f.read())
    print('Last 10 lines of events.ndjson:')
    with open(sc.events_file, 'r') as f:
        lines = f.readlines()
        for line in lines[-10:]:
            print(line.strip())
