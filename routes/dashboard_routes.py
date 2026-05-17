"""
Dashboard Routes
Handles the main dashboard page rendering.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from modules.data_manager import filter_active_tasks, load_assignments, load_exams, load_settings, save_assignments, save_exams
from modules.scheduler import generate_schedule
from modules.stress_calculator import calculate_stress
from modules.ai_summarizer import generate_study_plan, parse_study_plan_text
from modules.study_plan_cache import (
    build_study_plan_signature,
    get_cached_study_plan,
    invalidate_cached_study_plan,
    save_cached_study_plan,
)
from datetime import datetime

dashboard_bp = Blueprint("dashboard", __name__)

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


def _get_alerts(assignments, exams):
    """Generate alerts for due assignments and upcoming exams."""
    today = datetime.today().date()
    alerts = []
    
    # Check assignments due soon (within 3 days)
    for a in assignments:
        try:
            deadline = datetime.strptime(a["deadline"], "%Y-%m-%d").date()
            days_left = (deadline - today).days
            if 0 <= days_left <= 3:
                alerts.append(f"Assignment '{a['title']}' is due in {days_left} day(s)!")
            elif days_left < 0:
                alerts.append(f"Assignment '{a['title']}' is overdue!")
        except:
            pass
    
    # Check upcoming exams (within 7 days)
    for e in exams:
        try:
            exam_date = datetime.strptime(e["exam_date"], "%Y-%m-%d").date()
            days_left = (exam_date - today).days
            if 0 <= days_left <= 7:
                alerts.append(f"Exam '{e['subject']}' is in {days_left} day(s)!")
        except:
            pass
    
    return alerts


@dashboard_bp.route("/")
def index():
    assignments = load_assignments()
    exams = load_exams()
    active_assignments = filter_active_tasks(assignments)
    active_exams = filter_active_tasks(exams)
    schedule = generate_schedule(active_assignments, active_exams)
    stress = calculate_stress(active_assignments, active_exams)
    alerts = _get_alerts(active_assignments, active_exams)
    study_plan = ""
    study_plan_sections = []
    settings = load_settings()

    today_schedule = schedule[0] if schedule else {
        "date": datetime.today().strftime("%a, %d %b"),
        "tasks": [],
        "exam_warning": False,
        "total_workload": 0,
    }
    today_iso = datetime.today().strftime("%Y-%m-%d")
    due_today_count = sum(1 for assignment in active_assignments if assignment.get("deadline") == today_iso)
    this_week_task_count = sum(len(day["tasks"]) for day in schedule)
    this_week_workload = round(sum(day["total_workload"] for day in schedule), 2)

    return render_template(
        "dashboard.html",
        assignments=active_assignments,
        exams=active_exams,
        schedule=schedule,
        stress=stress,
        alerts=alerts,
        study_plan=study_plan,
        study_plan_sections=study_plan_sections,
        settings=settings,
        today_schedule=today_schedule,
        due_today_count=due_today_count,
        this_week_task_count=this_week_task_count,
        this_week_workload=this_week_workload,
        student_name="Researcher",
        active_page="dashboard",
        calendar_items=build_calendar_items(assignments, exams),
    )


@dashboard_bp.route("/study-plan")
def study_plan_page():
    assignments = load_assignments()
    exams = load_exams()
    active_assignments = filter_active_tasks(assignments)
    active_exams = filter_active_tasks(exams)
    schedule = generate_schedule(active_assignments, active_exams)
    stress = calculate_stress(active_assignments, active_exams)
    plan_signature = build_study_plan_signature(active_assignments, active_exams)
    study_plan = get_cached_study_plan(plan_signature)
    study_plan_sections = parse_study_plan_text(study_plan)
    settings = load_settings()

    today_schedule = schedule[0] if schedule else {
        "date": datetime.today().strftime("%a, %d %b"),
        "tasks": [],
        "exam_warning": False,
        "total_workload": 0,
    }
    this_week_task_count = sum(len(day["tasks"]) for day in schedule)
    this_week_workload = round(sum(day["total_workload"] for day in schedule), 2)

    return render_template(
        "study_plan.html",
        assignments=active_assignments,
        exams=active_exams,
        schedule=schedule,
        study_plan=study_plan,
        study_plan_sections=study_plan_sections,
        can_generate_study_plan=bool(active_assignments or active_exams),
        study_plan_needs_generation=not bool(study_plan),
        settings=settings,
        today_schedule=today_schedule,
        this_week_task_count=this_week_task_count,
        this_week_workload=this_week_workload,
        active_page="study_plan",
        calendar_items=build_calendar_items(active_assignments, active_exams),
    )


@dashboard_bp.route("/study-plan/generate", methods=["POST"])
def generate_study_plan_page():
    assignments = filter_active_tasks(load_assignments())
    exams = filter_active_tasks(load_exams())

    if not assignments and not exams:
        invalidate_cached_study_plan()
        return redirect(url_for("dashboard.study_plan_page"))

    stress = calculate_stress(assignments, exams)
    study_plan = generate_study_plan(assignments, exams, stress)
    plan_signature = build_study_plan_signature(assignments, exams)
    save_cached_study_plan(plan_signature, study_plan)
    return redirect(url_for("dashboard.study_plan_page"))


@dashboard_bp.route("/pomodoro")
def pomodoro_page():
    assignments = filter_active_tasks(load_assignments())
    exams = filter_active_tasks(load_exams())
    return render_template(
        "pomodoro.html",
        active_page="pomodoro",
        calendar_items=build_calendar_items(assignments, exams),
    )


@dashboard_bp.route("/api/toggle_status", methods=["POST"])
def toggle_status():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    item_id = data.get("item_id")
    is_done = data.get("is_done")
    
    if not item_id:
        return jsonify({"error": "Missing item_id"}), 400
        
    if str(item_id).startswith("assignment-"):
        real_id = str(item_id).replace("assignment-", "")
        assignments = load_assignments()
        for a in assignments:
            if str(a.get("id")) == real_id:
                a["status"] = "Done" if is_done else "Pending"
                break
        save_assignments(assignments)
        invalidate_cached_study_plan()
        return jsonify({"success": True, "type": "assignment"})
        
    elif str(item_id).startswith("exam-"):
        real_id = str(item_id).replace("exam-", "")
        exams = load_exams()
        for e in exams:
            if str(e.get("id")) == real_id:
                e["status"] = "Done" if is_done else "Pending"
                break
        save_exams(exams)
        invalidate_cached_study_plan()
        return jsonify({"success": True, "type": "exam"})
        
    return jsonify({"error": "Unknown item type"}), 400
