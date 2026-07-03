# ---------------------------------------------------------------
# backend/db/jobs.py
# WHY THIS FILE EXISTS:
#   One place that handles reading and writing job records.
#   The employer portal (React) talks to Flask routes, and those
#   routes call these functions. No job query logic lives anywhere
#   else, mirroring how candidates.py works for candidates.
#
# WHAT IT DOES:
#   - Creates a new job when an employer fills the "Create Job" form
#   - Lists all jobs for the "View Jobs" page
#   - Fetches one job by its id (needed when publishing)
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - Imports the shared `jobs` collection from connection.py
#   - routes/jobs.py (Member 1) calls these for the employer portal
#   - On publish, the required_skill from a job is passed to
#     candidates.find_candidates_by_skill() to decide who gets
#     a WhatsApp alert.
# ---------------------------------------------------------------

from bson import ObjectId
from db.connection import jobs


def create_job(title, company, required_skill, description):
    """
    Create a new job from the employer's "Create Job" form.
    required_skill is the field matched against each candidate's
    main_skill when the job is published, so it must be stored.
    published = False until the employer clicks "Publish Job".
    """
    new_job = {
        "title": title,
        "company": company,
        "required_skill": required_skill,  # matched against candidates
        "description": description,
        "published": False,                # becomes True on publish
    }
    result = jobs.insert_one(new_job)
    # Return the new job's id as a string so React can use it.
    return str(result.inserted_id)


def get_all_jobs():
    """
    Return every job, newest first, for the "View Jobs" page.
    MongoDB's _id is an ObjectId (not JSON-friendly), so we convert
    it to a string on each job before returning.
    """
    all_jobs = list(jobs.find().sort("_id", -1))
    for job in all_jobs:
        job["_id"] = str(job["_id"])
    return all_jobs


def get_job(job_id):
    """
    Fetch a single job by its id. Used when the employer publishes
    a job, so we can read its required_skill and mark it published.
    Returns None if the id doesn't exist.
    """
    job = jobs.find_one({"_id": ObjectId(job_id)})
    if job:
        job["_id"] = str(job["_id"])
    return job


def mark_published(job_id):
    """
    Flag a job as published after alerts have been sent, so the
    portal can show which jobs are live.
    """
    jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"published": True}},
    )