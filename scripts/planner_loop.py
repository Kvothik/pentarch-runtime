import sys
sys.path.insert(0, "/Users/sixx/.openclaw/workspace")

import os
import time
import json
import subprocess
import logging
from runtime.state_controller import StateController

PLANNER_INTERVAL_SECONDS = int(os.getenv('PLANNER_INTERVAL_SECONDS', '3600'))
LOG_FILE = '/Users/sixx/.openclaw/workspace/planner/planner_loop.log'

logging.basicConfig(filename=LOG_FILE,
                    level=logging.INFO,
                    format='[%(asctime)s] %(message)s')

def run_planner_scan():
    logging.info('Starting planner repo scan...')
    subprocess.run(['python3', '/Users/sixx/.openclaw/workspace/_beacon_local/scripts/planner_scan_repo.py'], check=True)
    logging.info('Planner repo scan completed.')

def convert_top_proposal():
    try:
        with open('/Users/sixx/.openclaw/workspace/planner/feature_proposals/repo_scan_report.json') as f:
            data = json.load(f)
        proposals = data.get('proposals', [])
        if not proposals:
            logging.info('No proposals found to convert.')
            return

        sc = StateController()

        # Backlog limit check
        backlog_active_count = sum(1 for t in sc.tasks.values() if t['state'] in ('backlog', 'active'))
        if backlog_active_count > 5:
            logging.info('[planner] skipped new proposal because backlog limit reached')
            return

        for p in proposals:
            task_id = p.get('title', 'untitled').lower().replace(' ', '-')
            if task_id in sc.tasks:
                logging.info(f'[planner] skipped duplicate proposal {task_id}')
                continue
            owner = p.get('owner', 'backend')
            details = p.copy()
            details.pop('title', None)
            details.pop('owner', None)

            try:
                sc.create_task(task_id, owner, details)
                sc.enqueue_task(task_id)
                logging.info(f'Converted top proposal into backlog task: {task_id}')
                break
            except Exception as e:
                logging.error(f'Failed to convert proposal {task_id}: {e}')
    except Exception as e:
        logging.error(f'Failed to convert top proposal: {e}')

def main_loop():
    while True:
        try:
            run_planner_scan()
            convert_top_proposal()
        except Exception as e:
            logging.error(f'Error in planner loop: {e}')
        time.sleep(PLANNER_INTERVAL_SECONDS)


if __name__ == '__main__':
    logging.info('Starting Sixx planner loop.')
    main_loop()
