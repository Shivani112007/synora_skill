from datetime import date

from flask import abort, flash, redirect, request, url_for

from app import (
    app,
    db,
    ensure_profile_fields,
    match_score,
    me,
    page,
)


@app.route("/opportunities")
def opportunities():
    u = me()
    if not u:
        return redirect(url_for("login"))
    ensure_profile_fields(u)
    q = request.args.get("q", "").strip().lower()
    typ = request.args.get("type", "").strip()
    all_ops = [o for o in db.all("opportunities") if o.get("active", True)]
    ranked = []
    for o in all_ops:
        haystack = " ".join(
            [
                o.get("title", ""),
                o.get("org", ""),
                o.get("type", ""),
                *o.get("skills", []),
            ]
        ).lower()
        if q and q not in haystack:
            continue
        if typ and o.get("type") != typ:
            continue
        ranked.append({**o, "score": match_score(u["skills"], o.get("skills", []))})
    ranked.sort(key=lambda o: (-o["score"], o.get("title", "").lower()))
    applied = {
        a["opp"]
        for a in db.all("applications")
        if a["student"] == u["id"] and a.get("status") != "Cancelled"
    }
    types = sorted({o.get("type", "") for o in all_ops if o.get("type")})
    return page(
        "opportunities.html",
        title="Opportunities",
        ranked=ranked,
        applied=applied,
        q=q,
        typ=typ,
        types=types,
    )


@app.route("/apply/<oid>", methods=["POST"])
def apply(oid):
    u = me()
    if not u:
        return redirect(url_for("login"))
    if u.get("role") != "student":
        abort(403)

    o = db.get("opportunities", oid)
    if not o or not o.get("active", True):
        flash("This opportunity is no longer available.")
        return redirect(url_for("opportunities"))

    # Enforce the deadline when it uses the format DD Mon YYYY.
    deadline_text = o.get("deadline", "").strip()
    if deadline_text:
        try:
            deadline_date = date.fromisoformat(deadline_text)
        except ValueError:
            try:
                from datetime import datetime

                deadline_date = datetime.strptime(deadline_text, "%d %b %Y").date()
            except ValueError:
                deadline_date = None

        if deadline_date and deadline_date < date.today():
            flash("The application deadline has passed.")
            return redirect(url_for("opportunities"))

    key = f"{u['id']}#{oid}"
    existing = db.get("applications", key)

    if existing and existing.get("status") != "Cancelled":
        flash("You already have an active application for this opportunity.")
        return redirect(url_for("applications"))

    if existing:
        existing.update({"company": o.get("org", ""), "status": "Submitted"})
        db.put("applications", existing)
        flash("You have successfully reapplied.")
    else:
        db.put(
            "applications",
            {
                "id": key,
                "student": u["id"],
                "opp": oid,
                "company": o.get("org", ""),
                "status": "Submitted",
            },
        )
        flash("Application submitted successfully.")

    return redirect(url_for("applications"))
