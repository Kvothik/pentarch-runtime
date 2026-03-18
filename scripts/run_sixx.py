import sys
import os

# Ensure workspace root is on path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from orchestrator.sixx import SixxOrchestrator

def main():
    orchestrator = SixxOrchestrator()
    orchestrator.run()

if __name__ == "__main__":
    main()
