from flask import jsonify, request

from app import app, match_score, page, split


@app.route("/")
def home():
    return page("home.html", title="SYNORA · Student Skill Platform")


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/api/match")
def api_match():
    skills, req = split(request.args.get("skills")), split(request.args.get("required"))
    return jsonify(score=match_score(skills, req))
