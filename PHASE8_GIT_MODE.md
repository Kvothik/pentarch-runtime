# Phase 8: Git/PR Mode Design Note

## Minimal Git Workflow for Workers

- Each task corresponds to a dedicated Git branch.
- Workers create branches at task start, naming branches to uniquely identify the task.
- Workers make changes needed to complete the task on their branch.
- Workers commit changes with commit messages referencing the task ID.
- Workers generate a change summary artifact describing modifications.
- Workers do NOT auto-push nor auto-open pull requests in this phase.

## Branch Creation

- Branches are created by workers at the start of task execution.
- Branch names follow the format:

  `task/<task_id>`

  where `<task_id>` uniquely identifies the task.

## Commit Message Format

- Commit messages are structured to include task context:

  `Task <task_id>: <concise description of work>`

  Example: `Task phase8-git-mode-123: Implement backend API authentication`

## Worker Output Summary

- Workers produce a JSON summary artifact after successful work containing:
  - Task ID
  - Branch name
  - Commit hash(es)
  - Change summary (list of files changed, key changes)

## Failure and Rollback

- On task failure, workers should abort changes and reset branch state.
- No automatic rollback or reverts are performed in this phase.
- Errors are reported in the task lifecycle and/or logs for manual intervention.

---

This design keeps the worker Git workflow lightweight and safe, deferring remote interaction and PR handling to later phases.
