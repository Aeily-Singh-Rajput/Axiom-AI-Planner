"""
Axiom Planner - Main Flask Application
Entry point for the app. Registers all routes.
"""

import os
import sys
from flask import Flask
from dotenv import load_dotenv

# Load local .env only for development
load_dotenv()

# Ensure project root is on sys.path
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

app.secret_key = os.getenv("SECRET_KEY", "dev_fallback_secret")

# Register Blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(assignment_bp)
app.register_blueprint(exam_bp)
app.register_blueprint(scheduler_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(settings_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # IMPORTANT for Railway
    app.run(host="0.0.0.0", port=port, debug=False)
