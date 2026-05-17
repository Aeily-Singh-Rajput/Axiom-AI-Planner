"""
Upload Routes
Handles PDF upload, text extraction, and AI summarization.
"""

import os
from flask import Blueprint, request, redirect, url_for, render_template, flash
from axiom_planner.modules.pdf_extractor import extract_text_from_pdf
from axiom_planner.modules.ai_summarizer import summarize_text
from axiom_planner.modules.data_manager import filter_active_tasks, load_assignments, save_assignments, load_exams
from axiom_planner.modules.study_plan_cache import invalidate_cached_study_plan

upload_bp = Blueprint("upload", __name__)

def build_calendar_items(assignments, exams):
    items = []
    for a in assignments:
        if a.get("deadline"):
            items.append({
                "id": f"assignment-{a.get('id')}",
                "date": a.get("deadline"),
                "title": a.get("title", "Assignment"),
                "type": "assignment",
            })
    for e in exams:
        if e.get("exam_date"):
            items.append({
                "id": f"exam-{e.get('id')}",
                "date": e.get("exam_date"),
                "title": e.get("subject", "Exam"),
                "type": "exam",
            })
    return items

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@upload_bp.route("/upload", methods=["GET"])
def upload_page():
    assignments = filter_active_tasks(load_assignments())
    exams = filter_active_tasks(load_exams())
    return render_template(
        "upload.html",
        assignments=assignments,
        exams=exams,
        active_page="upload",
        calendar_items=build_calendar_items(assignments, exams),
    )


@upload_bp.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    assignment_id = request.form.get("assignment_id")
    file = request.files.get("pdf_file")

    if not file or file.filename == "":
        flash("No file selected.")
        return redirect(url_for("upload.upload_page"))

    # Save the uploaded PDF temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text:
        flash("Could not extract text from PDF.")
        return redirect(url_for("upload.upload_page"))

    # -------------------------------------------------------
    # The summarize_text() function uses Google Gemini via the API key
    # configured in modules/ai_summarizer.py.
    # -------------------------------------------------------
    summary = summarize_text(extracted_text)

    # Save summary back to the assignment when provided
    assignments = load_assignments()
    if assignment_id:
        for a in assignments:
            if a["id"] == assignment_id:
                a["summary"] = summary
                break
        save_assignments(assignments)
        invalidate_cached_study_plan()

    active_assignments = filter_active_tasks(assignments)
    exams = filter_active_tasks(load_exams())

    # Clean up uploaded file
    os.remove(file_path)

    return render_template(
        "upload.html",
        assignments=active_assignments,
        exams=exams,
        summary=summary,
        active_page="upload",
        calendar_items=build_calendar_items(active_assignments, exams),
    )
