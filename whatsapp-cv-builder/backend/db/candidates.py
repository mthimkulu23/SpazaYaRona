# ---------------------------------------------------------------
# backend/db/candidates.py
# WHY THIS FILE EXISTS:
#   One place that handles reading and writing candidate records.
#   The WhatsApp bot (webhook) calls these functions so that no
#   database query logic is scattered across the rest of the code.
#
# WHAT IT DOES:
#   - Starts a new candidate when they first message the bot
#   - Saves each of the five answers as they come in
#   - Tracks which question comes next (the "step" field)
#   - Saves the OpenAI summary after the last answer
#   - Finds candidates whose skill matches a published job
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - Imports the shared `candidates` collection from connection.py
#   - webhook.py (Member 1) calls these to run the conversation
#   - matching.py calls find_candidates_by_skill() when a job is
#     published, to decide who receives a WhatsApp alert
#
# KEY DESIGN DECISION:
#   A candidate is uniquely identified by their WhatsApp sender
#   number (whatsapp_number). This is auto-captured from the
#   incoming message, NOT typed by the candidate. Job alerts are
#   sent to this number. The typed "Phone Number" (question 2) is
#   stored separately as a plain CV field.
# ---------------------------------------------------------------

from db.connection import candidates


def get_candidate(whatsapp_number):
    """
    Return the candidate record for this WhatsApp number, or None
    if they have never messaged before. Used at the start of every
    incoming message to see if we already know this person.
    """
    return candidates.find_one({"whatsapp_number": whatsapp_number})


def create_candidate(whatsapp_number):
    """
    Create a fresh candidate record the first time someone messages.
    step = 1 means the next answer we expect is question 1 (Full Name).
    All answer fields start empty and get filled in one at a time.
    """
    new_candidate = {
        "whatsapp_number": whatsapp_number,  # unique key + alert target
        "full_name": "",                     # question 1
        "phone_number": "",                  # question 2 (typed CV field)
        "qualification": "",                 # question 3
        "main_skill": "",                    # question 4
        "years_experience": "",              # question 5
        "summary": "",                       # filled by OpenAI after Q5
        "step": 1,                           # which question comes next
    }
    candidates.insert_one(new_candidate)
    return new_candidate


def save_answer(whatsapp_number, field, value, next_step):
    """
    Save one answer and move the candidate to the next question.
    - field: which column to fill (e.g. "full_name")
    - value: what the candidate typed
    - next_step: the question number to expect next
    Using $set updates only that one field and leaves the rest alone.
    """
    candidates.update_one(
        {"whatsapp_number": whatsapp_number},
        {"$set": {field: value, "step": next_step}},
    )


def save_summary(whatsapp_number, summary):
    """
    Save the OpenAI-generated professional summary after the
    candidate has answered all five questions. step = 6 marks the
    conversation as complete (there is no question 6).
    """
    candidates.update_one(
        {"whatsapp_number": whatsapp_number},
        {"$set": {"summary": summary, "step": 6}},
    )


def find_candidates_by_skill(skill):
    """
    Find every completed candidate whose main_skill contains the
    given skill (case-insensitive substring match). Called when an
    employer publishes a job, to decide who gets a WhatsApp alert.

    Example: job skill "React" matches a candidate whose main_skill
    is "React.js developer".

    step = 6 ensures we only alert candidates who finished all five
    questions (we don't message half-finished records).
    """
    return list(
        candidates.find({
            "main_skill": {"$regex": skill, "$options": "i"},
            "step": 6,
        })
    )