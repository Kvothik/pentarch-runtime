# SIXX Hydration Index

This document indexes canonical documentation for the Pentarch runtime system to be used for agent hydration on startup.

## Canonical Documentation References

- PHASE6_NOTE.md
- PHASE7_PLANNER.md
- PHASE8_GIT_MODE.md
- GITHUB_ISSUE_WORKFLOW.md
- docs/agent_architecture.md
- docs/agent_execution_rules.md
- docs/agent_workflow.md
- docs/github_issue_board_plan.md
- runtime/validation_tracker.py
- runtime/validation_tracker_integration.py

## Startup Checklist

Agents should report the following before acting:
- Current working directory
- Git repository root
- Target repository (Beacon product or Pentarch runtime)
- Current execution phase
- Currently active task

Ensure environment and paths are properly configured before operations.

---

## CRITICAL SYSTEM RULES (LOAD ON START)

- Beacon product repo path:
 /Users/sixx/.openclaw/workspace/beacon

- All product code MUST exist only in Beacon

- pentarch-runtime MUST NEVER contain:
 - backend/
 - mobile/
 - product docs

- After EVERY completed task:
 - git add .
 - git commit
 - git push

This is only for keeping the Beacon repository code in sync.
GitHub issues and boards are not part of execution.

Execution source of truth:
 /Users/sixx/.openclaw/workspace/pentarch-runtime/planner/planner_tasks.json

No other system (GitHub, docs, or boards) determines execution state.

After each task return:
- completed_task
- current_task_status
- next_task_from_queue
- blocker_or_none




This index is maintained within the Pentarch runtime repository.
