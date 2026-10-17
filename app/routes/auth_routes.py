from flask import flash, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app import ADMIN_EMAIL, app, db, page


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash(
                "Please provide a name, valid email and password of at least 6 characters."
            )
            return redirect(url_for("register"))
        if db.get("students", email):
            flash("Email already registered. Please sign in.")
            return redirect(url_for("login"))
        db.put(
            "students",
            {
                "id": email,
                "name": name,
                "pw": generate_password_hash(password),
                "role": "admin" if email == ADMIN_EMAIL else "student",
                "skills": [],
                "projects": [],
                "certificates": [],
                "interests": [],
                "achievements": [],
                "education": [],
            },
        )
        session["user"] = email
        flash("Welcome to SYNORA. Your portfolio is ready to build.")
        return redirect(url_for("dashboard"))
    return page("register.html", title="Create Account")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = db.get("students", request.form.get("email", "").strip().lower())
        if u and check_password_hash(u["pw"], request.form.get("password", "")):
            session["user"] = u["id"]
            return redirect(url_for("dashboard"))
        flash("Invalid credentials. Please check your email and password.")
    return page("login.html", title="Sign In")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
