# ---------------------------------------------------------------
# backend/routes/jobs.py
# WHY THIS FILE EXISTS:
#   These are the web endpoints the React employer portal calls to
#   create jobs, view jobs, and publish jobs. This is the bridge
#   between the employer's browser and our MongoDB + matching logic.
#
# WHAT IT DOES (three endpoints):
#   - POST /jobs                -> create a new job
#   - GET  /jobs                -> list all jobs
#   - POST /jobs/<id>/publish   -> publish a job, then find matching
#                                  candidates and WhatsApp them
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - Uses db/jobs.py for all database work (create/list/fetch/mark)
#   - Uses services/matching.py to alert candidates on publish
#   - Registered in app.py as a Blueprint (we uncomment that next)
#   - React's api.js (Member 3) calls these three URLs
#
# NOTE ON BLUEPRINTS:
#   A Flask "Blueprint" is just a group of routes in their own file,
#   so app.py stays clean. app.py registers this blueprint so these
#   URLs become live.
# ---------------------------------------------------------------

from flask import Blueprint, request, jsonify

from db.jobs import create_job, get_all_jobs, get_job, mark_published
from services.matching import notify_matching_candidates

# Create the blueprint. All routes below attach to it.
jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/jobs", methods=["POST"])
def create_job_route():
    """
    Create a new job from the employer's form.
    Expects JSON: { title, company, required_skill, description }
    Returns the new job's id.
    """
    data = request.get_json()

    # Basic validation: the fields we need must be present.
    # We keep it simple — just check they're not empty.
    title = data.get("title", "").strip()
    company = data.get("company", "").strip()
    required_skill = data.get("required_skill", "").strip()
    description = data.get("description", "").strip()

    if not title or not company or not required_skill:
        return jsonify({"error": "title, company and required_skill are required"}), 400

    job_id = create_job(title, company, required_skill, description)
    return jsonify({"message": "Job created", "job_id": job_id}), 201


@jobs_bp.route("/jobs", methods=["GET"])
def list_jobs_route():
    """
    Return all jobs (newest first) for the View Jobs page.
    """
    return jsonify(get_all_jobs()), 200


@jobs_bp.route("/jobs/<job_id>/publish", methods=["POST"])
def publish_job_route(job_id):
    """
    Publish a job: mark it published, then find matching candidates
    and send each one a WhatsApp alert. Returns how many were alerted.
    """
    job = get_job(job_id)
    if job is None:
        return jsonify({"error": "Job not found"}), 404

    # Mark the job as published in the database.
    mark_published(job_id)

    # Find matching candidates and send WhatsApp alerts.
    # Returns the number of candidates successfully alerted.
    alerted = notify_matching_candidates(job)

    return jsonify({
        "message": "Job published",
        "candidates_alerted": alerted,
    }), 200