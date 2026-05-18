# Notification Microservice

This microservice provides assignment notifications for a task manager application. It uses a REST API over HTTP and sends/receives JSON data.

## Features

- Get assignment notifications for a specific user
- Filter notifications by status: `read` or `unread`
- Filter notifications by priority: `High`, `Medium`, or `Low`
- Sort notifications so `High` priority appears first
- Create a new assignment notification
- Mark a notification as read
- Delete a notification for testing or cleanup

## Requirements

- Python 3.10 or newer
- Flask
- Flask-CORS
- requests
- pytest

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

For macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the microservice

```bash
python app.py
```

The service runs at:

```text
http://127.0.0.1:5000
```

## API Endpoints

### 1. Get notifications

```http
GET /notifications?user_id=25
```

Optional filters:

```http
GET /notifications?user_id=25&status=unread
GET /notifications?user_id=25&priority=High
```

Example response:

```json
{
  "success": true,
  "count": 1,
  "notifications": [
    {
      "id": 1,
      "user_id": "25",
      "title": "CS361 Assignment 6",
      "due_date": "2026-05-20",
      "priority": "High",
      "status": "unread",
      "message": "Assignment due soon"
    }
  ]
}
```

### 2. Create a notification

```http
POST /notifications
```

Required JSON body:

```json
{
  "user_id": 25,
  "title": "CS361 Sprint 2 Plan",
  "due_date": "2026-05-20",
  "priority": "High",
  "message": "Finish the notification microservice."
}
```

### 3. Mark a notification as read

```http
PATCH /notifications/1/read
```

### 4. Delete a notification

```http
DELETE /notifications/1
```

## Run the client example

Open one terminal and run:

```bash
python app.py
```

Open another terminal and run:

```bash
python client_example.py
```

## Run tests

```bash
pytest
```
