import os
import json
import logging
import threading
import requests
from typing import Optional

logging.basicConfig(level=logging.INFO)

GITHUB_API_URL = "https://api.github.com/graphql"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_PROJECT_ID = os.getenv("GITHUB_PROJECT_ID")

# Expected project column IDs to be configured as environment vars or loaded dynamically
COLUMN_BACKLOG = os.getenv("COLUMN_BACKLOG")
COLUMN_IN_PROGRESS = os.getenv("COLUMN_IN_PROGRESS")
COLUMN_VERIFYING = os.getenv("COLUMN_VERIFYING")
COLUMN_DONE = os.getenv("COLUMN_DONE")
COLUMN_FAILED = os.getenv("COLUMN_FAILED")

COLUMN_MAPPING = {
    "backlog": COLUMN_BACKLOG,
    "active": COLUMN_IN_PROGRESS,
    "verifying": COLUMN_VERIFYING,
    "accepted": COLUMN_DONE,
    "failed": COLUMN_FAILED,
}

EVENTS_FILE = "runtime/state/events.ndjson"
LOG = logging.getLogger("github_board_sync")

class GitHubBoardSync:
    def __init__(self):
        self.lock = threading.Lock()
        self.last_pos = 0

    def run(self):
        self.verify_environment()
        while True:
            self.process_new_events()

    def verify_environment(self):
        missing = []
        for var in ["GITHUB_TOKEN", "GITHUB_PROJECT_ID", "COLUMN_BACKLOG", "COLUMN_IN_PROGRESS", "COLUMN_VERIFYING", "COLUMN_DONE", "COLUMN_FAILED"]:
            if not os.getenv(var):
                missing.append(var)
        if missing:
            LOG.error(f"Missing required env vars for GitHub sync: {missing}")
            raise RuntimeError(f"Missing required env vars: {missing}")

    def process_new_events(self):
        with self.lock:
            try:
                with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                    f.seek(self.last_pos)
                    new_lines = f.readlines()
                    self.last_pos = f.tell()
                for line in new_lines:
                    if line.strip():
                        event = json.loads(line)
                        self.handle_event(event)
            except FileNotFoundError:
                LOG.warning("Events file not found yet.")

    def handle_event(self, event):
        event_type = event.get("event")
        task_id = event.get("task_id") or event.get("details", {}).get("task_id")
        if not task_id or not event_type:
            return
        target_column_id = COLUMN_MAPPING.get(self.state_for_event(event_type, event))
        if not target_column_id:
            LOG.debug(f"No column mapped for event type {event_type}")
            return
        # Find card id for task
        card_id = self.find_card_id_for_task(task_id)
        if not card_id:
            LOG.info(f"No existing card for task_id {task_id}, skipping GitHub move")
            return
        # Move card in GitHub Project
        self.move_card_to_column(card_id, target_column_id)

    def state_for_event(self, event_type: str, event: dict) -> Optional[str]:
        # Map event type to task state for board projection
        if event_type == "TASK_STATE_CHANGED":
            return event.get("new_state")
        elif event_type == "WORKER_DONE":
            return "verifying"
        elif event_type == "TASK_ACCEPTED":
            return "accepted"
        elif event_type == "WORKER_FAILURE" or event_type == "TASK_BLOCKED":
            return "failed"
        else:
            return None

    def find_card_id_for_task(self, task_id: str) -> Optional[str]:
        # Use GitHub API to find ProjectCard by task_id
        query = """
        query ($projectId: ID!, $taskId: String!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(query: $taskId, first: 10) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      id
                      title
                    }
                  }
                }
              }
            }
          }
        }
        """
        variables = {"projectId": GITHUB_PROJECT_ID, "taskId": task_id}
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.inertia-preview+json",
        }
        r = requests.post(GITHUB_API_URL, json={"query": query, "variables": variables}, headers=headers)
        if r.status_code != 200:
            LOG.error(f"GitHub API error finding card: {r.status_code} {r.text}")
            return None
        data = r.json()
        items = data.get("data", {}).get("node", {}).get("items", {}).get("nodes", [])
        for item in items:
            content = item.get("content")
            if content and content.get("title") == task_id:
                return item.get("id")
        return None

    def move_card_to_column(self, card_id: str, column_id: str):
        mutation = """
        mutation moveCard($cardId: ID!, $columnId: ID!) {
          moveProjectCard(input: {cardId: $cardId, columnId: $columnId}) {
            clientMutationId
          }
        }
        """
        variables = {"cardId": card_id, "columnId": column_id}
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.inertia-preview+json",
        }
        r = requests.post(GITHUB_API_URL, json={"query": mutation, "variables": variables}, headers=headers)
        if r.status_code != 200:
            LOG.error(f"GitHub API error moving card: {r.status_code} {r.text}")
        else:
            LOG.info(f"Moved card {card_id} to column {column_id}")


# To start sync in a separate thread or process:
# from _beacon_local.orchestrator.github_board_sync import GitHubBoardSync
# sync = GitHubBoardSync()
# import threading
# t = threading.Thread(target=sync.run)
# t.start()
