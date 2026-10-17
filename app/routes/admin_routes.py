import uuid
from datetime import date

from flask import abort, flash, redirect, request, url_for

from app import (
    app,
    db,
    ensure_profile_fields,
    me,
    page,
    parse_deadline,
    split,
)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    u = me()
    if not u or u["role"] != "admin":
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        org = request.form.get("org", "").strip()
        skills = split(request.form.get("skills"))
        if not title or not org or not skills:
            flash("Title, organization and required skills are required.")
            return redirect(url_for("admin"))
        db.put("opportunities", {
            "id": uuid.uuid4().hex[:8], "title": title, "type": request.form.get("type", "Internship"),
            "org": org, "skills": skills, "location": request.form.get("location", "").strip(),
            "deadline": request.form.get("deadline", "").strip(), "duration": request.form.get("duration", "").strip()
        })
        flash("Opportunity published successfully.")
        return redirect(url_for("admin"))
    students = [ensure_profile_fields(s) for s in db.all("students")]
    ops = [
        o for o in db.all("opportunities")
        if o.get("active", True)
    ]
    skill_set = {x.lower() for s in students for x in s.get("skills", [])}
    stats = {
        "students": sum(1 for s in students if s.get("role") == "student"),
        "opportunities": len(ops),
        "skills": len(skill_set),
        "active": sum(
            1 for o in ops
            if not o.get("deadline")
            or (
                parse_deadline(o.get("deadline"))
                and parse_deadline(o.get("deadline")) >= date.today()
            )
        )
    }
    return page('admin.html', title="Admin Control Center", students=students, ops=ops, stats=stats)


@app.route("/admin/opportunities/<oid>/edit", methods=["GET", "POST"])
def edit_opportunity(oid):
    u = me()
    if not u or u.get("role") != "admin":
        abort(403)

    o = db.get("opportunities", oid)
    if not o:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        org = request.form.get("org", "").strip()
        skills = split(request.form.get("skills"))

        if not title or not org or not skills:
            flash("Title, organization and required skills are required.")
            return redirect(url_for("edit_opportunity", oid=oid))

        o.update({
            "title": title,
            "org": org,
            "type": request.form.get("type", "Internship"),
            "location": request.form.get("location", "").strip(),
            "deadline": request.form.get("deadline", "").strip(),
            "duration": request.form.get("duration", "").strip(),
            "skills": skills
        })
        db.put("opportunities", o)
        flash("Opportunity updated successfully.")
        return redirect(url_for("admin"))

    return page('edit_opportunity.html',
        title="Edit Opportunity",
        o=o
    )


@app.route("/admin/opportunities/<oid>/delete", methods=["POST"])
def delete_opportunity(oid):
    u = me()
    if not u or u.get("role") != "admin":
        abort(403)

    o = db.get("opportunities", oid)
    if not o:
        abort(404)

    # Soft delete: preserve the opportunity and its application history.
    o["active"] = False
    db.put("opportunities", o)

    flash("Opportunity removed from student listings.")
    return redirect(url_for("admin"))
