import json
import os
from datetime import datetime
LOG_FILE = "log.json"
def log_activity(entry: dict):
    entry_copy = entry.copy()
    entry_copy["timestamp"] = datetime.now().isoformat()
    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    logs.append(entry_copy)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)
