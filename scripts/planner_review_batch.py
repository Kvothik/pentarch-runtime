import os
import json
import shutil
from datetime import datetime

INBOX_DIR = "/Users/sixx/.openclaw/workspace/planner/ui_reviews/inbox"
PROCESSED_DIR = "/Users/sixx/.openclaw/workspace/planner/ui_reviews/processed"
REPORTS_DIR = "/Users/sixx/.openclaw/workspace/planner/ui_reviews/reports"

os.makedirs(INBOX_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


def load_metadata(batch_path):
    metadata_file = os.path.join(batch_path, "metadata.json")
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    return metadata


def analyze_batch(batch_path):
    metadata = load_metadata(batch_path)
    batch_id = metadata.get("batch_id")

    # Placeholder for actual analysis logic - simulate empty lists
    ui_issues = []
    workflow_issues = []
    improvement_opportunities = []
    recommended_tasks = []

    # Example recommended task (to illustrate format)
    if metadata.get('image_files'):
        recommended_tasks.append({
            "title": f"Review UI for {batch_id}",
            "owner": "qa",
            "type": "ui_improvement",
            "evidence": "Screenshots indicate potential UI flow problems.",
            "problem": "Users report confusion navigating the app.",
            "proposal": "Revise onboarding screens to improve clarity.",
            "priority": "medium",
            "acceptance_criteria": [
                "Onboarding screens updated",
                "User testing confirms improved navigation"
            ]
        })

    report = {
        "batch_id": batch_id,
        "ui_issues": ui_issues,
        "workflow_issues": workflow_issues,
        "improvement_opportunities": improvement_opportunities,
        "recommended_tasks": recommended_tasks
    }
    return report


def save_report(report):
    report_file = os.path.join(REPORTS_DIR, f"review_{report['batch_id']}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    return report_file


def process_batch(batch_folder):
    batch_path = os.path.join(INBOX_DIR, batch_folder)
    if not os.path.isdir(batch_path):
        raise ValueError("Batch path is not a directory")

    metadata = load_metadata(batch_path)
    report = analyze_batch(batch_path)
    report_file = save_report(report)

    # Move batch folder to processed
    processed_path = os.path.join(PROCESSED_DIR, batch_folder)
    shutil.move(batch_path, processed_path)

    return report_file


if __name__ == '__main__':
    # Process all batches in inbox
    batches = [b for b in os.listdir(INBOX_DIR) if os.path.isdir(os.path.join(INBOX_DIR, b))]
    for batch_folder in batches:
        print(f"Processing batch {batch_folder}...")
        try:
            report_file = process_batch(batch_folder)
            print(f"Saved report to: {report_file}")
        except Exception as e:
            print(f"Error processing batch {batch_folder}: {e}")
