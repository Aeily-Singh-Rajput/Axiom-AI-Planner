import json
import os
import uuid
from flask import session, has_request_context

DATA_DIR = "data"

os.makedirs(DATA_DIR, exist_ok=True)

def _get_filepath(base_filename):
    """Generate a file path specific to the current user session."""
    if has_request_context():
        if "user_id" not in session:
            session["user_id"] = uuid.uuid4().hex
        user_id = session["user_id"]
        return os.path.join(DATA_DIR, f"{user_id}_{base_filename}")
    else:
        # Fallback if called outside a request context
        return os.path.join(DATA_DIR, f"default_{base_filename}")

def _read_json(filepath):
    """Read JSON file. Returns empty list if file doesn't exist."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)


def _write_json(filepath, data):
    """Write data to JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def load_assignments():
    return _read_json(_get_filepath("assignments.json"))


def save_assignments(assignments):
    _write_json(_get_filepath("assignments.json"), assignments)


def is_completed_task(task):
    """Return True when a saved assignment or exam should be hidden from planning."""
    return str(task.get("status", "")).strip().lower() in {"done", "completed"}


def filter_active_tasks(tasks):
    """Keep only tasks that still need planning or reminders."""
    return [task for task in tasks if not is_completed_task(task)]


def load_exams():
    return _read_json(_get_filepath("exams.json"))


def save_exams(exams):
    _write_json(_get_filepath("exams.json"), exams)


def load_settings():
    """Load user settings. Returns default settings if file doesn't exist."""
    filepath = _get_filepath("settings.json")
    settings = _read_json(filepath)
    if not settings:
        settings = {
            "profile_picture": None,
            "notifications_enabled": True,
            "email_notifications": False,
            "theme": "light"
        }
        save_settings(settings)
    return settings


def save_settings(settings):
    _write_json(_get_filepath("settings.json"), settings)
