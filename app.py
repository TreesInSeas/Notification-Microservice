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
@app.route("/notifications", methods=["GET"])
def get_notifications():
    user_id = request.args.get("user_id")
    status = request.args.get("status")
    priority = request.args.get("priority")

    if not user_id:
        return error_response("Missing required parameter: user_id")

    if status and status not in VALID_STATUSES:
        return error_response("Invalid status. Use 'read' or 'unread'.")

    if priority and priority not in VALID_PRIORITIES:
        return error_response("Invalid priority. Use 'High', 'Medium', or 'Low'.")

    notifications = load_notifications()

    results = [
        notification for notification in notifications
        if str(notification.get("user_id")) == str(user_id)
    ]

    if status:
        results = [notification for notification in results if notification.get("status") == status]

    if priority:
        results = [notification for notification in results if notification.get("priority") == priority]

    # User story requirement: High priority notifications should appear first.
    results.sort(key=lambda item: (PRIORITY_ORDER.get(item.get("priority"), 99), item.get("due_date", "")))

    return jsonify({
        "success": True,
        "notifications": results
    }), 200
