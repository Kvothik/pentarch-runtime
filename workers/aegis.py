from runtime.state_controller import StateController

sc = StateController()

def execute(task_id):
    print(f"Aegis worker executing task {task_id}")

    worker_id = None
    for wid, info in sc.workers.items():
        if info['task_id'] == task_id:
            worker_id = wid
            break
    if not worker_id:
        print(f"Aegis: no worker_id linked to task {task_id}")
        return 'failure'

    print(f"Aegis worker {worker_id} running task {task_id}")
    try:
        sc.record_worker_done(worker_id)
        print(f"Aegis worker {worker_id}: reported done")
        return 'success'
    except Exception as e:
        print(f"Aegis worker {worker_id}: failed to report done {e}")
        return 'failure'
