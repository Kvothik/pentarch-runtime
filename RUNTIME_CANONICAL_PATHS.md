# Runtime Canonical Paths

## Canonical Runtime Files

- Orchestrator:
  - _beacon_local/orchestrator/sixx.py

- Runtime Controller:
  - runtime/state_controller.py

- Worker Modules:
  - _beacon_local/workers/forge.py
  - _beacon_local/workers/atlas.py
  - _beacon_local/workers/aegis.py
  - _beacon_local/workers/sentinel.py

- Runtime State Files:
  - runtime/state/tasks.json
  - runtime/state/workers.json
  - runtime/state/events.ndjson
  - runtime/state/events.offset
  - runtime/state/pulse.json

- Scripts for Run/Reset/Setup:
  - _beacon_local/scripts/run_sixx.py
  - _beacon_local/scripts/reset_state.py (if exists)
  - _beacon_local/scripts/setup_phase4_test.py
  - _beacon_local/scripts/setup_phase5_test.py (if exists)

## Non-Canonical / Legacy Duplicates

- Any copies or duplicates of the above paths located elsewhere that have been used in the past but should be deprecated and no longer edited.

## Rules

- All future runtime changes must target the canonical file paths only.
- Do not edit files inside the Beacon app repo for runtime logic.
- Do not rename, move, or extensively refactor current directory/package structures in this pass.

