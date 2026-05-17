from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from datetime import datetime, timezone
import json

app = Flask(__name__)
CORS(app)

DATA_FILE = Path(__file__).parent / "notifications.json"
VALID_PRIORITIES = {"High", "Medium", "Low"}
VALID_STATUSES = {"read", "unread"}
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

def load_notifications():
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []

def save_notifications(notifications):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(notifications, file, indent=2)


def get_next_id(notifications):
    if not notifications:
        return 1
    return max(notification["id"] for notification in notifications) + 1

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "service": "Notification Microservice",
        "endpoints": [
            "GET /notifications?user_id=<id>",
            "POST /notifications",
            "PATCH /notifications/<notification_id>/read"
        ]
    })
