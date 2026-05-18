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
