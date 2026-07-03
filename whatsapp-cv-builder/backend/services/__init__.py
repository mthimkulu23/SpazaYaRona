# ---------------------------------------------------------------
# backend/services/conversation.py
# WHY THIS FILE EXISTS:
#   This is the "brain" of the WhatsApp bot. It runs the five-question
#   flow: given an incoming message, it figures out which question the
#   candidate is answering, saves that answer, and returns the next
#   question to ask.
#
# WHAT IT DOES:
#   - First message from a new number -> create their record, ask Q1
#   - Each following message -> save the answer, advance to next Q
#   - After Q5 -> trigger the OpenAI summary and finish
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - Uses db/candidates.py to read and write candidate records
#   - Uses the "step" field on each candidate to track progress
#   - Calls services/openai_service.py to build the summary after Q5
#   - routes/webhook.py calls handle_message() for every incoming
#     WhatsApp message and sends the returned text back to the user
#
# DESIGN NOTE:
#   whatsapp_number is auto-captured from the incoming message (the
#   sender), NOT typed. Question 2 ("Phone Number") is stored as a
#   normal CV field. Job alerts later go to whatsapp_number.
# ---------------------------------------------------------------

from db.candidates import (
    get_candidate,
    create_candidate,
    save_answer,
    save_summary,
)
from services.openai_service import generate_summary

# The five questions, in order. Each entry maps a step number to:
#   - the field name in the candidate record to save the answer into
#   - the question text to send for THAT step
# Step 1 is asked when the candidate is first created.
QUESTIONS = {
    1: {"field": "full_name",        "text": "Question 1 of 5:\nWhat is your full name?"},
    2: {"field": "phone_number",     "text": "Question 2 of 5:\nWhat is your phone number?"},
    3: {"field": "qualification",    "text": "Question 3 of 5:\nWhat is your highest qualification?"},
    4: {"field": "main_skill",       "text": "Question 4 of 5:\nWhat is your main skill? (e.g. Plumbing, React, Sales)"},
    5: {"field": "years_experience", "text": "Question 5 of 5:\nHow many years of experience do you have?"},
}


def handle_message(whatsapp_number, message_text):
    """
    Handle one incoming WhatsApp message and return the text to reply.

    whatsapp_number: the sender's number (auto-captured, our unique key)
    message_text:    what the candidate typed

    Returns a plain string that webhook.py will send back to the user.
    """

    candidate = get_candidate(whatsapp_number)

    # --- CASE 1: brand new person messaging for the first time ---
    # We don't treat their first message as an answer. We create their
    # record and ask Question 1.
    if candidate is None:
        create_candidate(whatsapp_number)
        return (
            "Welcome to the CV Builder!\n"
            "I'll ask you 5 quick questions to build your CV.\n\n"
            + QUESTIONS[1]["text"]
        )

    current_step = candidate["step"]

    # --- CASE 2: they already finished all five questions ---
    # step 6 means complete. Don't re-run the flow.
    if current_step >= 6:
        return (
            "Your CV is already complete! "
            "You'll receive a WhatsApp alert when a matching job is posted."
        )

    # --- CASE 3: they are answering the current question ---
    # Save their answer into the field for the current step.
    field = QUESTIONS[current_step]["field"]
    save_answer(whatsapp_number, field, message_text, current_step + 1)

    # If that was NOT the last question, ask the next one.
    if current_step < 5:
        next_step = current_step + 1
        return QUESTIONS[next_step]["text"]

    # --- CASE 4: that was Question 5 — the flow is finished ---
    # Re-read the candidate so we have all five saved answers, generate
    # the summary with OpenAI, save it, and send it back.
    candidate = get_candidate(whatsapp_number)
    summary = generate_summary(candidate)
    save_summary(whatsapp_number, summary)

    return (
        "Thank you! Your CV is complete.\n\n"
        "Here is your professional summary:\n\n"
        + summary
        + "\n\nYou'll get a WhatsApp alert when a matching job is posted."
    )