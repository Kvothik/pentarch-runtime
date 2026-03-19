from runtime.state_controller import StateController

def execute(task_id):
    print(f"[Forge] execute called for task {task_id}")

    # Re-read state at execution time, not import time
    sc = StateController()

    worker_id = None
    for wid, info in sc.workers.items():
        if info.get('task_id') == task_id:
            worker_id = wid
            print(f"[Forge] Resolved worker_id from workers.json: {worker_id}")
            break

    # Fallback: task record may already carry worker_id
    if not worker_id:
        task = sc.tasks.get(task_id, {})
        worker_id = task.get("worker_id")
        if worker_id:
            print(f"[Forge] Resolved worker_id from tasks.json: {worker_id}")

    if not worker_id:
        err_msg = f"[Forge] ERROR - no worker_id linked to task {task_id}"
        print(err_msg)
        raise ValueError(err_msg)

    print("[Forge] Before record_worker_done call")
    sc.record_worker_done(worker_id)
    print(f"[Forge] Worker {worker_id}: reported done")
    print("[Forge] After record_worker_done call")
    return "success"
