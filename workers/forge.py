import json
from runtime.state_controller import StateController
import requests
import os

sc = StateController()

upload_log_file = "/Users/sixx/.openclaw/workspace/upload_debug_log.json"

# Patch requests.post to capture upload call info
original_post = requests.post

def patched_post(url, *args, **kwargs):
    result = original_post(url, *args, **kwargs)
    if "/documents" in url:
        try:
            upload_info = {
                "url": url,
                "method": "POST",
                "packet_id": url.split('/')[5] if len(url.split('/')) > 5 else None,
                "file_metadata": kwargs.get('files', None),
                "status_code": result.status_code,
                "response_body": result.text,
            }
            with open(upload_log_file, "w") as f:
                json.dump(upload_info, f, indent=2)
        except Exception as e:
            print(f"[Forge] Failed to log upload info: {e}")
    return result

requests.post = patched_post

def execute(task_id):
    print(f"[Forge] Executing task {task_id} with worker")

    worker_id = None
    for wid, info in sc.workers.items():
        if info['task_id'] == task_id:
            worker_id = wid
            break

    if not worker_id:
        err_msg = f"[Forge] ERROR - no worker_id linked to task {task_id}"
        print(err_msg)
        return {'status': 'error', 'message': err_msg}

    try:
        sc.record_worker_done(worker_id)
        print(f"[Forge] Worker {worker_id}: reported done")
    except Exception as e:
        print(f"[Forge] Worker {worker_id}: record_worker_done raised: {e}")
        return {'status': 'error', 'message': str(e)}

    print(f"[Forge] execute done {task_id}")

    return {'status': 'success', 'task_id': task_id}
