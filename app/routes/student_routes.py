from flask import flash, redirect, request, url_for

from app import (
    app,
    db,
    ensure_profile_fields,
    match_score,
    me,
    page,
    profile_completion,
    split,
)


@app.route("/dashboard")
def dashboard():
    u = me()
    if not u:
        return redirect(url_for("login"))
    ensure_profile_fields(u)
    apps = [a for a in db.all("applications") if a["student"] == u["id"]]
    ranked = sorted(
        (
            {**o, "score": match_score(u["skills"], o.get("skills", []))}
            for o in db.all("opportunities")
            if o.get("active", True)
        ),
        key=lambda o: -o["score"],
    )
    return page(
        "dashboard.html",
        title="Dashboard",
        u=u,
        completion=profile_completion(u),
        application_count=len(apps),
        recommended=ranked,
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    u = me()
    if not u:
        return redirect(url_for("login"))
    ensure_profile_fields(u)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            u["name"] = name
        u["skills"] = split(request.form.get("skills"))
        u["interests"] = split(request.form.get("interests"))
        db.put("students", u)
        flash("Profile saved successfully.")
        return redirect(url_for("profile"))
    return page(
        "profile.html", title="My Portfolio", u=u, completion=profile_completion(u)
    )


@app.route("/portfolio/<kind>/add", methods=["POST"])
def portfolio_add(kind):
    allowed = {"projects", "certificates", "achievements", "education"}
    u = me()
    if not u:
        return redirect(url_for("login"))
    if kind not in allowed:
        return redirect(url_for("profile"))
    value = request.form.get("value", "").strip()
    if not value:
        flash("Please enter a value before adding it.")
    else:
        ensure_profile_fields(u)
        u[kind].append(value)
        db.put("students", u)
        flash(
            f"{kind.capitalize()[:-1] if kind.endswith('s') else kind.capitalize()} added."
        )
    return redirect(url_for("profile"))


@app.route("/portfolio/<kind>/delete/<int:index>", methods=["POST"])
def portfolio_delete(kind, index):
    allowed = {"projects", "certificates", "achievements", "education"}
    u = me()
    if not u:
        return redirect(url_for("login"))
    ensure_profile_fields(u)
    if kind in allowed and 0 <= index < len(u[kind]):
        u[kind].pop(index)
        db.put("students", u)
        flash("Portfolio item removed.")
    return redirect(url_for("profile"))
