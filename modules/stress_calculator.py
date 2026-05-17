"""Academic stress scoring for the dashboard.

The score is intentionally deterministic: deadlines, task type, difficulty,
overlap, overdue work, and completion all move the result in predictable ways.
"""

from datetime import datetime
from modules.data_manager import is_completed_task


def _days_until(date_str):
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (target - datetime.today().date()).days
    except Exception:
        return 999


def _deadline_urgency(days_left):
    if days_left < 0:
        return 35
    if days_left <= 1:
        return 50
    if days_left <= 3:
        return 30
    if days_left <= 7:
        return 15
    if days_left <= 14:
        return 8
    return 5


def _difficulty_weight(value):
    try:
        difficulty = int(value)
    except Exception:
        difficulty = 1
    return {1: 5, 2: 10, 3: 20, 4: 30}.get(difficulty, 10)


def _assignment_type_weight(assignment):
    title = assignment.get("title", "").lower()
    try:
        size = int(assignment.get("size", 1))
    except Exception:
        size = 1

    if "quiz" in title:
        return 5, "Quiz"
    if "project" in title:
        return 35, "Project"
    if size >= 3:
        return 25, "Large assignment"
    if size == 2:
        return 18, "Assignment"
    return 15, "Small assignment"


def _completion_factor(task):
    if is_completed_task(task):
        return 0
    try:
        progress = float(task.get("progress", 0))
    except Exception:
        progress = 0
    progress = max(0, min(100, progress))
    return max(0.1, 1 - (progress / 100))


def _classify(score):
    if score >= 86:
        return {
            "level": "Extreme",
            "emoji": "😫",
            "message": "Extreme pressure detected — protect today for urgent deadlines first.",
            "recommendation": "Choose one exam or overdue task and start a focused session now.",
        }
    if score >= 66:
        return {
            "level": "High",
            "emoji": "😟",
            "message": "Heavy workload detected this week.",
            "recommendation": "Prioritize the closest exam or the hardest assignment today.",
        }
    if score >= 41:
        return {
            "level": "Medium",
            "emoji": "😐",
            "message": "Upcoming deadlines may require focus.",
            "recommendation": "Break large tasks into smaller sessions and keep steady momentum.",
        }
    if score >= 21:
        return {
            "level": "Low",
            "emoji": "🙂",
            "message": "Your workload is present, but still manageable.",
            "recommendation": "Start early and keep one calm study block on the calendar.",
        }
    return {
        "level": "Very Low",
        "emoji": "😌",
        "message": "You’re in a calm study zone today.",
        "recommendation": "Maintain the rhythm with a light review or planning session.",
    }


def calculate_stress(assignments, exams):
    raw_score = 0
    reasons = []
    dated_items = []

    for assignment in assignments:
        completion = _completion_factor(assignment)
        if completion <= 0:
            continue

        days_left = _days_until(assignment.get("deadline"))
        type_weight, type_label = _assignment_type_weight(assignment)
        item_score = (
            _deadline_urgency(days_left)
            + type_weight
            + _difficulty_weight(assignment.get("difficulty"))
        ) * completion
        raw_score += item_score
        dated_items.append(("assignment", days_left))

        if days_left < 0:
            reasons.append(f"{type_label} '{assignment.get('title', 'Assignment')}' is overdue")
        elif days_left <= 1:
            reasons.append(f"{type_label} deadline is extremely close")
        elif days_left <= 3:
            reasons.append(f"{type_label} deadline is approaching fast")

    for exam in exams:
        if is_completed_task(exam):
            continue
        days_left = _days_until(exam.get("exam_date"))
        item_score = _deadline_urgency(days_left) + 40 + 20
        raw_score += item_score
        dated_items.append(("exam", days_left))
        if days_left < 0:
            reasons.append(f"Exam '{exam.get('subject', 'Exam')}' has passed")
        elif days_left <= 1:
            reasons.append("Exam is extremely close")
        elif days_left <= 7:
            reasons.append("Exam preparation window is narrowing")

    close_items = [item for item in dated_items if 0 <= item[1] <= 3]
    if len(close_items) >= 2:
        raw_score += 20
        reasons.append("Multiple deadlines are colliding this week")
    if any(item[0] == "exam" and 0 <= item[1] <= 2 for item in dated_items) and any(
        item[0] == "assignment" and 0 <= item[1] <= 2 for item in dated_items
    ):
        raw_score += 20
        reasons.append("Exam and assignment overlap detected")

    score = min(100, round(raw_score))
    classified = _classify(score)

    return {
        "level": classified["level"],
        "score": score,
        "emoji": classified["emoji"],
        "message": classified["message"],
        "recommendation": classified["recommendation"],
        "reasons": reasons if reasons else ["Workload is manageable"],
    }
