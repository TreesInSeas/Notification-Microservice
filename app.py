from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
from datetime import datetime, timezone
import json
import re

app = Flask(__name__)
CORS(app)

DATA_FILE = Path(__file__).parent / "notifications.json"
VALID_PRIORITIES = {"High", "Medium", "Low"}
VALID_STATUSES = {"read", "unread"}
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def error_response(message, status_code=400):
    return jsonify({"success": False, "error": message}), status_code


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_notifications():
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_notifications(notifications):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(notifications, file, indent=2, ensure_ascii=False)


def get_next_id(notifications):
    if not notifications:
        return 1
    return max(int(notification.get("id", 0)) for notification in notifications) + 1


def sort_notifications(notifications):
    return sorted(
        notifications,
        key=lambda item: (
            PRIORITY_ORDER.get(item.get("priority"), 99),
            item.get("due_date", "9999-99-99"),
            int(item.get("id", 0)),
        ),
    )


def validate_notification_data(data):
    required_fields = ["user_id", "title", "due_date", "priority", "message"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return f"Missing required field(s): {', '.join(missing_fields)}"

    if str(data["user_id"]).strip() == "":
        return "user_id cannot be empty."

    if str(data["title"]).strip() == "":
        return "title cannot be empty."

    if len(str(data["title"])) > 120:
        return "title must be 120 characters or fewer."

    if not DATE_PATTERN.match(str(data["due_date"])):
        return "due_date must use YYYY-MM-DD format."

    if data["priority"] not in VALID_PRIORITIES:
        return "Invalid priority. Use 'High', 'Medium', or 'Low'."

    if len(str(data["message"])) > 500:
        return "message must be 500 characters or fewer."

    return None


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "service": "Notification Microservice",
        "description": "Provides assignment notifications for a task manager application.",
        "endpoints": {
            "get_notifications": "GET /notifications?user_id=<id>&status=<read|unread>&priority=<High|Medium|Low>",
            "create_notification": "POST /notifications",
            "mark_read": "PATCH /notifications/<notification_id>/read",
            "delete_notification": "DELETE /notifications/<notification_id>"
        }
    }), 200


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

    results = sort_notifications(results)

    return jsonify({
        "success": True,
        "count": len(results),
        "notifications": results
    }), 200


@app.route("/notifications", methods=["POST"])
def create_notification():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return error_response("Request body must be valid JSON.")

    validation_error = validate_notification_data(data)
    if validation_error:
        return error_response(validation_error)

    notifications = load_notifications()

    new_notification = {
        "id": get_next_id(notifications),
        "user_id": str(data["user_id"]).strip(),
        "title": str(data["title"]).strip(),
        "due_date": str(data["due_date"]).strip(),
        "priority": data["priority"],
        "status": "unread",
        "message": str(data["message"]).strip(),
        "created_at": utc_now(),
        "read_at": None
    }

    notifications.append(new_notification)
    save_notifications(notifications)

    return jsonify({
        "success": True,
        "message": "Notification created successfully.",
        "notification": new_notification
    }), 201


@app.route("/notifications/<int:notification_id>/read", methods=["PATCH"])
def mark_notification_as_read(notification_id):
    notifications = load_notifications()

    for notification in notifications:
        if int(notification.get("id", -1)) == notification_id:
            notification["status"] = "read"
            notification["read_at"] = utc_now()
            save_notifications(notifications)
            return jsonify({
                "success": True,
                "message": "Notification marked as read.",
                "notification": notification
            }), 200

    return error_response("Notification not found.", 404)


@app.route("/notifications/<int:notification_id>", methods=["DELETE"])
def delete_notification(notification_id):
    notifications = load_notifications()
    new_notifications = [
        notification for notification in notifications
        if int(notification.get("id", -1)) != notification_id
    ]

    if len(new_notifications) == len(notifications):
        return error_response("Notification not found.", 404)

    save_notifications(new_notifications)
    return jsonify({
        "success": True,
        "message": "Notification deleted."
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
