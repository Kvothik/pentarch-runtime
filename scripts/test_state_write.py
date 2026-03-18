import sys
sys.path.insert(0, "/Users/sixx/.openclaw/workspace")

from runtime.state_controller import StateController

sc = StateController()

print('[Test] Creating task phase4-event-test-1')
sc.create_task('phase4-event-test-1', owner='backend')
print('[Test] create_task completed')

abs_path = sc.events_file
print(f'[Test] Events file at: {abs_path}')
try:
    size = os.path.getsize(abs_path)
    print(f'[Test] Events file size: {size}')
except Exception as e:
    print(f'[Test] Could not get file size: {e}')

with open(abs_path, 'r') as f:
    lines = f.readlines()
    print('[Test] Last 5 lines of events.ndjson:')
    for line in lines[-5:]:
        print(line.strip())
