import os
import json

REPORT_FILE = "/Users/sixx/.openclaw/workspace/planner/feature_proposals/repo_scan_report.json"
REPO_ROOT = "/Users/sixx/.openclaw/workspace"

CATEGORY_MAP = {
    "feature": "feature ideas",
    "workflow": "workflow improvements",
    "devexp": "developer experience improvements",
    "ui": "UI improvements",
    "arch": "architecture suggestions",
    "test": "testing gaps"
}


def analyze_repo(root_path):
    proposals = []
    categories_found = set()

    # Scan top-level directories and files
    entries = os.listdir(root_path)
    
    # Example checks (simplified):
    if 'docs' in entries:
        categories_found.add("documentation")
        proposals.append({
            "title": "Improve project documentation",
            "owner": "architecture",
            "type": "feature",
            "evidence": "docs folder present",
            "problem": "Documentation is incomplete or could be better organized.",
            "proposal": "Revise and enhance architecture and API docs for accuracy and clarity.",
            "priority": "medium",
            "acceptance_criteria": [
                "Clear, organized docs",
                "Updated API references"
            ]
        })
    if 'scripts' in entries:
        categories_found.add("workflow")
        proposals.append({
            "title": "Enhance automation scripts",
            "owner": "backend",
            "type": "workflow_improvement",
            "evidence": "scripts folder present",
            "problem": "Some build and deployment automation can be improved.",
            "proposal": "Refactor and optimize scripts for better reliability and efficiency.",
            "priority": "high",
            "acceptance_criteria": [
                "Improved script reliability",
                "Reduced manual steps"
            ]
        })
    if 'tests' not in entries:
        categories_found.add("testing gaps")
        proposals.append({
            "title": "Create initial test suites",
            "owner": "qa",
            "type": "testing gaps",
            "evidence": "missing /tests folder",
            "problem": "Lack of automated testing coverage.",
            "proposal": "Develop unit and integration tests to cover core functionality.",
            "priority": "high",
            "acceptance_criteria": [
                "Test coverage > 80%",
                "All critical features covered"
            ]
        })
    if 'ui' in entries or 'frontend' in entries:
        categories_found.add("ui")
        proposals.append({
            "title": "Improve front-end UI responsiveness",
            "owner": "mobile",
            "type": "ui_improvement",
            "evidence": "ui or frontend folder detected",
            "problem": "UI has responsiveness performance issues.",
            "proposal": "Optimize front-end code and assets.",
            "priority": "medium",
            "acceptance_criteria": [
                "Reduced UI latency",
                "Enhanced responsiveness on mobile"
            ]
        })

    return proposals, list(categories_found)


def save_report(proposals):
    with open(REPORT_FILE, 'w') as f:
        json.dump({"proposals": proposals}, f, indent=2)
    print(f"Saved repo scan report with {len(proposals)} proposals to {REPORT_FILE}")


if __name__ == '__main__':
    proposals, categories = analyze_repo(REPO_ROOT)
    save_report(proposals)
    print(f"Categories detected: {categories}")
    print(f"Number of proposals generated: {len(proposals)}")
    if proposals:
        print(f"Example proposal JSON:\n{json.dumps(proposals[0], indent=2)}")
