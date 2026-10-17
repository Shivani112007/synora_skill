"""SYNORA Flask application factory and shared helpers."""
import os
from datetime import date, datetime
from flask import Flask, render_template
from app.config import Config
from app.models import Store

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
ADMIN_EMAIL = Config.ADMIN_EMAIL
S3_BUCKET = Config.S3_BUCKET
AWS_REGION = Config.AWS_REGION
MAX_UPLOAD_SIZE = Config.MAX_CONTENT_LENGTH
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
TABLES = ("students", "opportunities", "applications")
db = Store()

def split(text):
    return [s.strip() for s in (text or "").replace("\n", ",").split(",") if s.strip()]

def parse_deadline(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d %b %Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None

def match_score(student_skills, required_skills):
    req = {s.strip().lower() for s in required_skills if s.strip()}
    if not req:
        return 0
    have = {s.strip().lower() for s in student_skills if s.strip()}
    return round(100 * len(req & have) / len(req))

def me():
    return db.get("students", __import__("flask").session["user"]) if "user" in __import__("flask").session else None

def ensure_profile_fields(u):
    for field in ("skills", "projects", "certificates", "interests", "achievements", "education"):
        u.setdefault(field, [])
    return u

def profile_completion(u):
    ensure_profile_fields(u)
    checks = [bool(u.get(k)) for k in ("name", "skills", "projects", "certificates", "achievements", "interests", "education")]
    return round(sum(checks) * 100 / len(checks))

def page(template_name, title="SYNORA", **ctx):
    body = render_template(template_name, **ctx)
    return render_template("base.html", title=title, body=body, u=me())

# Import route modules to register their URL rules.
from app.routes import public_routes, auth_routes, student_routes, opportunity_routes, application_routes, admin_routes, document_routes  # noqa: E402,F401
