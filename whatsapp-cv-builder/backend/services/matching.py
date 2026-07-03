# ---------------------------------------------------------------
# backend/services/matching.py
# WHY THIS FILE EXISTS:
#   This is the "System matches candidates" step of the demo. When
#   an employer publishes a job, this file finds candidates whose
#   skill matches the job and sends each of them a WhatsApp alert.
#
# WHAT IT DOES:
#   - Takes a job (which has a required_skill)
#   - Finds all COMPLETED candidates whose main_skill matches
#     (case-insensitive substring, e.g. job "React" matches
#      candidate "React.js developer")
#   - Sends each matched candidate a WhatsApp job alert
#   - Returns how many candidates were alerted
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - Uses db/candidates.py -> find_candidates_by_skill() (already tested)
#   - Uses services/whatsapp_service.py -> send_message() (already tested)
#   - routes/jobs.py calls notify_matching_candidates() when the
#     employer clicks "Publish Job"
# ---------------------------------------------------------------

from db.candidates import find_candidates_by_skill
from services.whatsapp_service import send_message


def notify_matching_candidates(job):
    """
    Find candidates matching a job's required skill and WhatsApp them.

    job: a job dict with "title", "company", and "required_skill".

    Returns the number of candidates that were alerted.
    """

    required_skill = job.get("required_skill", "")

    # Safety: if the job has no skill, there's nothing to match on.
    if not required_skill:
        return 0

    # Find every completed candidate whose main_skill contains the
    # job's required skill. This reuses the tested function in
    # candidates.py (which also filters to step == 6, i.e. finished).
    matches = find_candidates_by_skill(required_skill)

    # Build the alert message once. It's the same text for everyone.
    alert_text = (
        "New job alert!\n\n"
        f"Position: {job.get('title', '')}\n"
        f"Company: {job.get('company', '')}\n"
        f"Skill needed: {required_skill}\n\n"
        "Reply YES if you're interested."
    )

    # Send the alert to each matched candidate's WhatsApp number.
    # We count how many we sent so routes/jobs.py can report it.
    sent_count = 0
    for candidate in matches:
        number = candidate.get("whatsapp_number", "")
        if number:
            success = send_message(number, alert_text)
            if success:
                sent_count += 1

    return sent_count