# SIXX Hydration Index

This document defines the canonical hydration model for Sixx and the Pentarch runtime.

## 1. Purpose

Hydration must give Sixx enough context to:
- operate the Pentarch runtime correctly
- preserve repo boundaries
- read the canonical task queue correctly
- load the right Beacon product context before building or validating app work

This file is the startup source for active operating context.

---

## 2. Canonical Paths

- Beacon product repo:
 /Users/sixx/.openclaw/workspace/beacon

- Pentarch runtime repo:
 /Users/sixx/.openclaw/workspace/pentarch-runtime

- Canonical execution queue:
 /Users/sixx/.openclaw/workspace/pentarch-runtime/planner/planner_tasks.json

---

## 3. Repo Boundary Rules

### Beacon may contain only:
- backend
- mobile
- infra
- datasets
- tests
- product docs/specs
- README.md
- .gitignore
- repo_map.md
- run-maestro.sh
- run-maestro-ios.sh
- run-maestro-android.sh

### Pentarch may contain only:
- orchestrator
- workers
- scripts
- planner
- runtime
- hydration/rule/system docs
- runtime test/support files

### Hard rules
- All product code MUST exist only in Beacon.
- Pentarch MUST NOT contain backend/, mobile/, or product docs/specs.
- Beacon MUST NOT contain runtime/orchestrator/planner/system files.
- Beacon root allowlist must pass before Beacon push.

---

## 4. Execution Source of Truth

Execution source of truth:
/Users/sixx/.openclaw/workspace/pentarch-runtime/planner/planner_tasks.json

No other system determines execution state.
Not GitHub.
Not boards.
Not docs.
Not chat history.

After hydration, Sixx must read the canonical queue directly and identify:
- current active task
- next queued task

---

## 5. Active Runtime Context To Load

On startup, Sixx should load only active Pentarch runtime context:

- RUNTIME_CANONICAL_PATHS.md
- PHASE7_PLANNER.md
- AGENTS.md
- README.md (if present and active)
- this file: SIXX_HYDRATION_INDEX.md

Do not load inactive or historical docs.
Do not load GitHub workflow docs as execution truth.
Do not load deprecated phase docs unless explicitly required for historical reference.

---

## 6. Beacon Product Context Policy

Hydration is not complete for app work until Sixx loads the Beacon product docs needed for the active task.

### Minimum Beacon product context for any dev task:
- repo_map.md
- docs/northstar.md
- docs/system_invariants.md

### Load task-specific Beacon docs based on task domain:

#### Backend / API / validation work
- docs/api_contracts.md
- docs/database_schema.md
- docs/error_policy.md

#### PDF / packet generation work
- docs/pdf_spec.md

#### TDCJ lookup / parser work
- docs/tdcj_lookup_adapter.md
- docs/tdcj_html_parser_spec.md

#### QA / regression / workflow validation work
- relevant tests
- relevant API/spec docs
- relevant feature docs tied to the active queued task

Sixx should load only the minimum Beacon docs required for the current queued task.

---

## 7. Startup Procedure

On every fresh start or rehydrate:

1. Read this file.
2. Confirm canonical Beacon path.
3. Confirm canonical Pentarch path.
4. Read the canonical queue directly.
5. Determine:
 - current active task
 - next task
6. Load only active Pentarch runtime docs.
7. Load only task-relevant Beacon product docs required for the active task.
8. Then execute.

---

## 8. Required Startup Report

After hydration, Sixx must report:

- hydration_loaded_yes_or_no
- canonical_queue_path
- current_task_or_none
- next_task_from_queue_or_none
- beacon_product_context_loaded_yes_or_no
- blocker_or_none

---

## 9. Hydration Reference Policy

- Only reference files that currently exist.
- Only reference files that are active in the current operating model.
- Do not reference inactive or historical docs as active guidance.
- Do not reference Beacon system/rule docs.
- If a referenced file is removed, moved, or becomes inactive, remove it from this index immediately.

---## 10. Task Completion Reporting

After each completed task return:

- completed_task
- current_task_status
- next_task_from_queue
- blocker_or_none

GitHub issues and boards are not part of execution truth.
Git is used only to keep the correct repo in sync.