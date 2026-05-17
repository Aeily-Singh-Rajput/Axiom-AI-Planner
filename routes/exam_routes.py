"""
Exam Routes
Handles adding and deleting exams.
"""

from flask import Blueprint, request, redirect, url_for
from axiom_planner.modules.data_manager import load_exams, save_exams
from axiom_planner.modules.study_plan_cache import invalidate_cached_study_plan
import uuid

exam_bp = Blueprint("exam", __name__)


@exam_bp.route("/add_exam", methods=["POST"])
def add_exam():
    exams = load_exams()

    new_exam = {
        "id": str(uuid.uuid4()),
        "subject": request.form.get("subject"),
        "exam_date": request.form.get("exam_date"),
        "syllabus": request.form.get("syllabus", ""),
    }

    exams.append(new_exam)
    save_exams(exams)
    invalidate_cached_study_plan()

    return redirect(url_for("dashboard.index"))


@exam_bp.route("/delete_exam/<exam_id>", methods=["POST"])
def delete_exam(exam_id):
    exams = load_exams()
    exams = [e for e in exams if e["id"] != exam_id]
    save_exams(exams)
    invalidate_cached_study_plan()
    return redirect(url_for("dashboard.index"))
