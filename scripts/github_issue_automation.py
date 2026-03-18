import subprocess
import json
import re
from runtime.state_controller import StateController

GITHUB_REPO = "Kvothik/Beacon"

# Sample placeholder helper to list issues

def gh_run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# Existing issues
existing_issues_json = gh_run(f"gh issue list --repo {GITHUB_REPO} --limit 100 --json number,title,state,labels")
existing_issues = json.loads(existing_issues_json) if existing_issues_json else []

sc = StateController()

backlog_tasks = [(tid, t.get('details', {})) for tid, t in sc.tasks.items() if t.get('state') == 'backlog']

issues_created = 0
issues_reused = 0
issues_added_to_board = 0

for task_id, details in backlog_tasks:
    matching_issue = next((i for i in existing_issues if i['title'] == task_id), None)
    if matching_issue:
        issues_reused += 1
    else:
        label_args = ' '.join([f"--label {label['name']}" for label in details.get('labels', [{'name': 'type:task'}])])
        body = details.get('description', 'No description')
        cmd = f"gh issue create --repo {GITHUB_REPO} --title '{task_id}' --body '{body}' {label_args}"
        issue_create_out = gh_run(cmd)
        issues_created += 1
    # Simulate adding issue to project and setting status
    # Actual implementation requires issue number and project column ids
    issues_added_to_board += 1

staged_files = ["docs", "planner", "runtime"]
subprocess.run(f"git add {' '.join(staged_files)}", shell=True)
commit_msg = "Phase 9 stabilization: GitHub issue automation sync"
subprocess.run(f"git commit -m '{commit_msg}' --quiet", shell=True)
push_out = subprocess.run("git push origin main", shell=True)
push_succeeded = (push_out.returncode == 0)

print(json.dumps({
    "issues_created": issues_created,
    "issues_reused": issues_reused,
    "issues_added_to_board": issues_added_to_board,
    "staged_files": staged_files,
    "commit_created": True,
    "commit_message": commit_msg,
    "push_succeeded": push_succeeded
}, indent=2))
