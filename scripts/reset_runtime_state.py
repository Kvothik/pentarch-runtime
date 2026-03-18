import os
import subprocess
import signal
import time

# Kill running Sixx processes
def kill_sixx_process():
    try:
        result = subprocess.run(['pgrep', '-f', 'scripts/run_sixx.py'], capture_output=True, text=True)
        pids = result.stdout.strip().split('\n') if result.stdout else []
        for pid in pids:
            if pid:
                os.kill(int(pid), signal.SIGTERM)
                print(f'Killed Sixx process with PID {pid}')
    except Exception as e:
        print(f'Error killing Sixx process: {e}')

# Reset runtime state

def reset_file(path, content=''):
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        size = os.path.getsize(path)
        print(f'{os.path.abspath(path)}: reset to size {size}')
        with open(path, 'r') as f:
            summary = f.read(300)
            print(f'Content:\n{summary}')
    except Exception as e:
        print(f'Error resetting {path}: {e}')


if __name__ == '__main__':
    kill_sixx_process()
    time.sleep(2)
    base_dir = "/Users/sixx/.openclaw/workspace/runtime/state"
    files = [
        ('tasks.json', '{}'),
        ('workers.json', '{}'),
        ('pulse.json', '{}'),
        ('events.ndjson', ''),
        ('events.offset', '0')
    ]
    for file, content in files:
        reset_file(os.path.join(base_dir, file[0]), content)
