"""
Settings Routes
Handles user settings, profile picture, and notifications.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from axiom_planner.modules.data_manager import filter_active_tasks, load_settings, save_settings, load_assignments, load_exams
import os
from werkzeug.utils import secure_filename

settings_bp = Blueprint("settings", __name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def build_calendar_items(assignments, exams):
    items = []
    for a in assignments:
        if a.get("deadline"):
            items.append({
                "date": a.get("deadline"),
                "title": a.get("title", "Assignment"),
                "type": "assignment",
            })
    for e in exams:
        if e.get("exam_date"):
            items.append({
                "date": e.get("exam_date"),
                "title": e.get("subject", "Exam"),
                "type": "exam",
            })
    return items

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@settings_bp.route("/settings")
def settings_page():
    settings = load_settings()
    assignments = filter_active_tasks(load_assignments())
    exams = filter_active_tasks(load_exams())
    return render_template(
        "settings.html",
        settings=settings,
        active_page="settings",
        calendar_items=build_calendar_items(assignments, exams),
    )


@settings_bp.route("/update_settings", methods=["POST"])
def update_settings():
    settings = load_settings()
    settings["notifications_enabled"] = "notifications_enabled" in request.form
    settings["email_notifications"] = "email_notifications" in request.form
    settings["theme"] = request.form.get("theme", "light")
    save_settings(settings)
    flash("Settings updated successfully!")
    return redirect(url_for("settings.settings_page"))


@settings_bp.route("/upload_profile", methods=["POST"])
def upload_profile():
    if 'profile_picture' not in request.files:
        flash("No file selected")
        return redirect(url_for("settings.settings_page"))
    
    file = request.files['profile_picture']
    if file.filename == '':
        flash("No file selected")
        return redirect(url_for("settings.settings_page"))
    
    if file and allowed_file(file.filename):
        filename = secure_filename("profile.jpg")  # Always save as profile.jpg
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        settings = load_settings()
        settings["profile_picture"] = f"/static/uploads/{filename}"
        save_settings(settings)
        
        flash("Profile picture updated!")
    else:
        flash("Invalid file type. Please upload PNG, JPG, JPEG, or GIF.")
    
    return redirect(url_for("settings.settings_page"))
