"""
Assignment Routes
Handles adding and deleting assignments.
"""

from flask import Blueprint, request, redirect, url_for
from axiom_planner.modules.data_manager import load_assignments, save_assignments
from axiom_planner.modules.study_plan_cache import invalidate_cached_study_plan
import uuid
from datetime import datetime

assignment_bp = Blueprint("assignment", __name__)


@assignment_bp.route("/add_assignment", methods=["POST"])
def add_assignment():
    assignments = load_assignments()

    new_assignment = {
        "id": str(uuid.uuid4()),
        "title": request.form.get("title"),
        "deadline": request.form.get("deadline"),
        "difficulty": int(request.form.get("difficulty", 1)),   # 1=Easy, 2=Medium, 3=Hard
        "size": int(request.form.get("size", 1)),               # 1=Small, 2=Medium, 3=Large
        "status": "Pending",
        "summary": "",
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }

    assignments.append(new_assignment)
    save_assignments(assignments)
    invalidate_cached_study_plan()

    return redirect(url_for("dashboard.index"))


@assignment_bp.route("/delete_assignment/<assignment_id>", methods=["POST"])
def delete_assignment(assignment_id):
    assignments = load_assignments()
    assignments = [a for a in assignments if a["id"] != assignment_id]
    save_assignments(assignments)
    invalidate_cached_study_plan()
    return redirect(url_for("dashboard.index"))
