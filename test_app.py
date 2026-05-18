import json
import app as notification_app


def setup_test_data(tmp_path, monkeypatch):
    test_file = tmp_path / "notifications.json"
    monkeypatch.setattr(notification_app, "DATA_FILE", test_file)
    test_file.write_text(json.dumps([
        {
            "id": 1,
            "user_id": "25",
            "title": "High Priority Assignment",
            "due_date": "2026-05-20",
            "priority": "High",
            "status": "unread",
            "message": "Important assignment",
            "created_at": "2026-05-18T00:00:00+00:00",
            "read_at": None
        },
        {
            "id": 2,
            "user_id": "25",
            "title": "Low Priority Reading",
            "due_date": "2026-05-21",
            "priority": "Low",
            "status": "unread",
            "message": "Optional reading",
            "created_at": "2026-05-18T00:00:00+00:00",
            "read_at": None
        },
        {
            "id": 3,
            "user_id": "99",
            "title": "Other User Task",
            "due_date": "2026-05-22",
            "priority": "Medium",
            "status": "unread",
            "message": "Different user",
            "created_at": "2026-05-18T00:00:00+00:00",
            "read_at": None
        }
    ]), encoding="utf-8")
    return test_file


def test_get_notifications_requires_user_id(tmp_path, monkeypatch):
    setup_test_data(tmp_path, monkeypatch)
    client = notification_app.app.test_client()

    response = client.get("/notifications")

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_get_notifications_returns_only_selected_user(tmp_path, monkeypatch):
    setup_test_data(tmp_path, monkeypatch)
    client = notification_app.app.test_client()

    response = client.get("/notifications?user_id=25")
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["count"] == 2
    assert all(item["user_id"] == "25" for item in data["notifications"])


def test_high_priority_appears_first(tmp_path, monkeypatch):
    setup_test_data(tmp_path, monkeypatch)
    client = notification_app.app.test_client()

    response = client.get("/notifications?user_id=25")
    notifications = response.get_json()["notifications"]

    assert notifications[0]["priority"] == "High"


def test_create_notification(tmp_path, monkeypatch):
    setup_test_data(tmp_path, monkeypatch)
    client = notification_app.app.test_client()

    response = client.post("/notifications", json={
        "user_id": 25,
        "title": "New Assignment",
        "due_date": "2026-05-23",
        "priority": "Medium",
        "message": "New task added"
    })
    data = response.get_json()

    assert response.status_code == 201
    assert data["success"] is True
    assert data["notification"]["status"] == "unread"
    assert data["notification"]["id"] == 4


def test_create_notification_rejects_bad_priority(tmp_path, monkeypatch):
    setup_test_data(tmp_path, monkeypatch)
    client = notification_app.app.test_client()

    response = client.post("/notifications", json={
        "user_id": 25,
        "title": "Bad Priority",
        "due_date": "2026-05-23",
        "priority": "Urgent",
        "message": "Bad priority value"
    })

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_mark_notification_as_read(tmp_path, monkeypatch):
    setup_test_data(tmp_path, monkeypatch)
    client = notification_app.app.test_client()

    response = client.patch("/notifications/1/read")
    data = response.get_json()

    assert response.status_code == 200
    assert data["success"] is True
    assert data["notification"]["status"] == "read"
    assert data["notification"]["read_at"] is not None
