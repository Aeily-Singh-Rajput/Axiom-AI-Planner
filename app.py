"""
Axiom Planner - Main Flask Application
Entry point for the app. Registers all routes.
"""

import os
from dotenv import load_dotenv
load_dotenv()
import sys
from flask import Flask

# Ensure the project root is on sys.path when running the app as a script
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from routes.dashboard_routes import dashboard_bp
from routes.assignment_routes import assignment_bp
from routes.exam_routes import exam_bp
from routes.scheduler_routes import scheduler_bp
from routes.upload_routes import upload_bp
from routes.settings_routes import settings_bp

app = Flask(__name__)
app.secret_key = "axiom_planner_secret"  # Change this in production

# Register Blueprints (modular routes)
app.register_blueprint(dashboard_bp)
app.register_blueprint(assignment_bp)
app.register_blueprint(exam_bp)
app.register_blueprint(scheduler_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(settings_bp)

if __name__ == "__main__":
    app.run(debug=True)
