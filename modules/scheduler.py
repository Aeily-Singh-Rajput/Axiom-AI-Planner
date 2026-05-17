"""
Scheduler Module
Distributes assignments across available days.
Reduces workload automatically when an exam is near.

Logic:
workload = difficulty × size
daily_work = workload ÷ available_days
If exam within 3 days → reduce daily work by 50%
"""

from datetime import datetime, timedelta
from modules.data_manager import filter_active_tasks


def _days_until(date_str):
    """Returns number of days from today until a given date string (YYYY-MM-DD)."""
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        return (target - today).days
    except Exception:
        return 999  # fallback: far future


def _nearest_exam_days(exams):
    """Returns days until the nearest upcoming exam. Returns None if no exams."""
    upcoming = [_days_until(e["exam_date"]) for e in exams if _days_until(e["exam_date"]) >= 0]
    return min(upcoming) if upcoming else None


def generate_schedule(assignments, exams):
    """
    Generates a day-by-day schedule for the next 7 days.
    Returns a list of dicts: [{date, tasks: [{title, daily_work}], exam_warning}]
    """
    assignments = filter_active_tasks(assignments)
    exams = filter_active_tasks(exams)

    today = datetime.today().date()
    nearest_exam = _nearest_exam_days(exams)
    schedule = []

    for day_offset in range(7):
        current_day = today + timedelta(days=day_offset)
        days_label = current_day.strftime("%a, %d %b")
        days_to_exam = (nearest_exam - day_offset) if nearest_exam is not None else None

        # Flag exam warning if exam is within 3 days from this day
        exam_warning = days_to_exam is not None and 0 <= days_to_exam <= 3

        tasks = []

        for a in assignments:
            deadline_days = _days_until(a["deadline"]) - day_offset
            if deadline_days < 0:
                continue  # already past deadline

            available_days = max(deadline_days, 1)
            workload = a["difficulty"] * a["size"]
            daily_work = round(workload / available_days, 2)

            # Reduce workload on exam-near days
            if exam_warning:
                daily_work = round(daily_work * 0.5, 2)

            if daily_work > 0:
                tasks.append({
                    "id": a.get("id"),
                    "title": a["title"],
                    "daily_work": daily_work,
                    "difficulty": a["difficulty"],
                    "size": a["size"],
                })

        schedule.append({
            "date": days_label,
            "tasks": tasks,
            "exam_warning": exam_warning,
            "total_workload": round(sum(t["daily_work"] for t in tasks), 2),
        })

    return schedule
