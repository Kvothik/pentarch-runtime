# Minimal runtime autonomy smoke test
from runtime.state_controller import StateController

def test_autonomous_queue_progression():
    sc = StateController()
    # Setup initial queue state with two tasks
    task1_id, task2_id = 'autotask1', 'autotask2'
    # Create first task
    if task1_id not in sc.tasks:
        sc.create_task(task1_id, owner='owner:backend')
        sc.enqueue_task(task1_id)
        sc.activate_task(task1_id)
    # Create second task
    if task2_id not in sc.tasks:
        sc.create_task(task2_id, owner='owner:backend')
        sc.enqueue_task(task2_id)

    # Link worker and mark first task as done
    sc.link_worker(task1_id, 'owner:backend-worker-autotask1')
    sc.record_worker_done('owner:backend-worker-autotask1')

    # Check that task1 transitions to delivered
    assert sc.tasks[task1_id]['state'] == 'delivered'

    # Check if task2 promoted to backlog
    assert sc.tasks[task2_id]['state'] == 'backlog'

    # Check if worker linked for task2 (simulate)
    sc.link_worker(task2_id, 'owner:backend-worker-autotask2')

    # Clean up
    del sc.tasks[task1_id]
    del sc.tasks[task2_id]
    del sc.workers['owner:backend-worker-autotask1']
    del sc.workers['owner:backend-worker-autotask2']
    sc._save_json(sc.tasks_file, sc.tasks)
    sc._save_json(sc.workers_file, sc.workers)

    print("Runtime autonomy smoke test completed successfully.")

if __name__ == '__main__':
    test_autonomous_queue_progression()
