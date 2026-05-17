"""
Scheduler Routes
Returns the generated schedule as JSON (for dynamic frontend use if needed).
"""

from flask import Blueprint, jsonify
from axiom_planner.modules.data_manager import filter_active_tasks, load_assignments, load_exams
from axiom_planner.modules.scheduler import generate_schedule

scheduler_bp = Blueprint("scheduler", __name__)


@scheduler_bp.route("/get_schedule")
def get_schedule():
    assignments = filter_active_tasks(load_assignments())
    exams = filter_active_tasks(load_exams())
    schedule = generate_schedule(assignments, exams)
    return jsonify(schedule)
