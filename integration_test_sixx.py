import runtime.state_controller as state_controller
import orchestrator.sixx as sixx_module
import time
import os

STATE_DIR = 'runtime/state'

def reset_runtime_state():
    files = ['tasks.json', 'workers.json', 'events.ndjson', 'pulse.json']
    for f in files:
        path = os.path.join(STATE_DIR, f)
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    # Recreate empty canonical state files
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(os.path.join(STATE_DIR, 'tasks.json'), 'w') as f:
        f.write('{}')
    with open(os.path.join(STATE_DIR, 'workers.json'), 'w') as f:
        f.write('{}')
    with open(os.path.join(STATE_DIR, 'events.ndjson'), 'w') as f:
        f.write('')
    with open(os.path.join(STATE_DIR, 'pulse.json'), 'w') as f:
        f.write('{}')


def seed_backlog_task():
    sc = state_controller.StateController(STATE_DIR)
    sc.create_task('integration-test-1', {'owner_label': 'owner:backend', 'desc': 'Integration test task'})
    sc._change_task_state('integration-test-1', 'backlog')


def run_orchestrator_once():
    sixx = sixx_module.SixxOrchestrator()
    # Run a single iteration of plan/dispatch/resolve
    # Remove polling-based plan/dispatch/resolve calls
    # Start full event-driven orchestration run loop
    sixx.run()
    return True


def print_state_files():
    with open(os.path.join(STATE_DIR, 'tasks.json')) as f:
        print('tasks.json:', f.read())
    with open(os.path.join(STATE_DIR, 'workers.json')) as f:
        print('workers.json:', f.read())
    with open(os.path.join(STATE_DIR, 'events.ndjson')) as f:
        print('events.ndjson:')
        for line in f:
            print(line.strip())


if __name__ == '__main__':
    reset_runtime_state()
    seed_backlog_task()
    success = run_orchestrator_once()
    print_state_files()
    # Verify desired final states
    sc = state_controller.StateController(STATE_DIR)
    task_accepted = (sc.tasks['integration-test-1']['state'] == 'accepted')
    worker_terminated = 'forge-test-worker' not in sc.workers or sc.workers.get('forge-test-worker', {}).get('state') == 'terminated'
    print(f'Task accepted: {task_accepted}')
    print(f'Worker terminated: {worker_terminated}')
    # Check for any illegal transitions (try except pattern)
    try:
        sc.accept_task('integration-test-1')  # Should raise error
        print('Illegal transition was allowed (Error)')
    except ValueError as e:
        print('Illegal transition rejected as expected:', str(e))
