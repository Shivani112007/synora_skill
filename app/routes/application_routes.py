from flask import abort, flash, redirect, request, url_for

from app import app, db, me, page


@app.route("/applications/<path:app_id>/cancel", methods=["POST"])
def cancel_application(app_id):
    u = me()
    if not u:
        return redirect(url_for("login"))
    if u.get("role") != "student":
        abort(403)

    a = db.get("applications", app_id)
    if not a or a.get("student") != u["id"]:
        abort(404)

    if a.get("status") != "Submitted":
        flash("Only submitted applications can be cancelled.")
        return redirect(url_for("applications"))

    a["status"] = "Cancelled"
    db.put("applications", a)

    flash("Application cancelled. You can reapply while the opportunity is available.")
    return redirect(url_for("applications"))


@app.route("/applications", methods=["GET", "POST"])
def applications():
    u = me()
    if not u:
        return redirect(url_for("login"))

    if request.method == "POST" and u.get("role") == "admin":
        a = db.get("applications", request.form.get("id", ""))
        status = request.form.get("status", "")
        allowed_statuses = {
            "Submitted",
            "Under Review",
            "Shortlisted",
            "Accepted",
            "Rejected",
            "Cancelled",
        }

        if a and status in allowed_statuses:
            a["status"] = status
            db.put("applications", a)
            flash("Application status updated.")
        else:
            flash("Invalid application or status.")

        return redirect(url_for("applications"))

    apps = (
        db.all("applications")
        if u.get("role") == "admin"
        else [a for a in db.all("applications") if a["student"] == u["id"]]
    )

    ops = db.all("opportunities")
    titles = {o["id"]: o["title"] for o in ops}
    companies = {o["id"]: o.get("org", "") for o in ops}
    active_opps = {o["id"] for o in ops if o.get("active", True)}

    # Backfill company names for old application records when rendered.
    for a in apps:
        if not a.get("company"):
            a["company"] = companies.get(a.get("opp"), "Unknown")

    return page(
        "applications.html",
        title="Applications",
        apps=apps,
        titles=titles,
        companies=companies,
        active_opps=active_opps,
        u=u,
    )
