import hashlib
import json
import os
from flask import has_request_context
from axiom_planner.modules.data_manager import _get_filepath, _read_json, _write_json


CACHE_FILENAME = "study_plan_cache.json"


def build_study_plan_signature(assignments, exams):
    """Create a stable fingerprint for the active planning inputs."""
    payload = {
        "assignments": [
            {
                "id": item.get("id"),
                "title": item.get("title"),
                "deadline": item.get("deadline"),
                "difficulty": item.get("difficulty"),
                "size": item.get("size"),
                "status": item.get("status"),
                "summary": item.get("summary"),
            }
            for item in assignments
        ],
        "exams": [
            {
                "id": item.get("id"),
                "subject": item.get("subject"),
                "exam_date": item.get("exam_date"),
                "syllabus": item.get("syllabus"),
                "status": item.get("status"),
            }
            for item in exams
        ],
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def get_cached_study_plan(signature):
    if not has_request_context():
        return None
    cache = _read_json(_get_filepath(CACHE_FILENAME))
    if not isinstance(cache, dict) or cache.get("signature") != signature:
        return None
    return cache.get("study_plan")


def save_cached_study_plan(signature, study_plan):
    if not has_request_context():
        return
    _write_json(
        _get_filepath(CACHE_FILENAME),
        {
            "signature": signature,
            "study_plan": study_plan,
        },
    )


def invalidate_cached_study_plan():
    if not has_request_context():
        return
    cache_path = _get_filepath(CACHE_FILENAME)
    if os.path.exists(cache_path):
        os.remove(cache_path)
