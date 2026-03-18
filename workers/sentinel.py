from runtime.state_controller import StateController


def execute(task_id):
    sc = StateController()

    worker_id = None
    for wid, info in sc.workers.items():
        if info['task_id'] == task_id:
            worker_id = wid
            break

    if not worker_id:
        return {'status': 'error', 'message': f'No worker_id linked to task {task_id}'}

    # Placeholder work
    print(f"[Sentinel] Executing task {task_id} with worker {worker_id}")

    sc.record_worker_done(worker_id)

    return {'status': 'success', 'task_id': task_id}
