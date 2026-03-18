from runtime.state_controller import StateController

sc = StateController()

def execute(task_id):
    print(f"[Forge] execute called for task {task_id}")

    worker_id = None
    for wid, info in sc.workers.items():
        if info['task_id'] == task_id:
            worker_id = wid
            print(f"[Forge] Resolved worker_id: {worker_id}")
            break
    if not worker_id:
        err_msg = f"[Forge] ERROR - no worker_id linked to task {task_id}"
        print(err_msg)
        raise ValueError(err_msg)

    print(f"[Forge] Before record_worker_done call")
    try:
        sc.record_worker_done(worker_id)
        print(f"[Forge] Worker {worker_id}: reported done")
    except Exception as e:
        print(f"[Forge] Worker {worker_id}: record_worker_done raised: {e}")
        raise

    print(f"[Forge] After record_worker_done call")

    return 'success'
