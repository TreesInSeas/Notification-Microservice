import requests

BASE_URL = "http://127.0.0.1:5000"
def get_notifications(user_id, status=None, priority=None):
    params = {"user_id": user_id}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority

    response = requests.get(f"{BASE_URL}/notifications", params=params)
    print("GET /notifications")
    print(response.status_code)
    print(response.json())
def create_notification(user_id, title, due_date, priority, message):
    response = requests.post(
        f"{BASE_URL}/notifications",
        json={
            "user_id": user_id,
            "title": title,
            "due_date": due_date,
            "priority": priority,
            "message": message,
        },
    )
    print("POST /notifications")
    print(response.status_code)
    print(response.json())
    return response.json().get("notification", {}).get("id")


def mark_as_read(notification_id):
    response = requests.patch(f"{BASE_URL}/notifications/{notification_id}/read")
    print("PATCH /notifications/<id>/read")
    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    get_notifications(user_id=25)

    new_id = create_notification(
        user_id=25,
        title="CS361 Sprint 2 Plan",
        due_date="2026-05-20",
        priority="High",
        message="Finish the notification microservice and upload it to GitHub.",
    )

    if new_id:
        mark_as_read(new_id)
        get_notifications(user_id=25, status="read")
