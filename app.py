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
