# ---------------------------------------------------------------
# backend/services/openai_service.py
# WHY THIS FILE EXISTS:
#   Turns a candidate's five answers into ONE short professional
#   CV summary using OpenAI. This is the only place the project
#   talks to OpenAI.
#
# WHAT IT DOES:
#   - Takes a candidate record (the five answers)
#   - Builds a simple prompt
#   - Calls the OpenAI chat API once
#   - Returns the summary as a plain string
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - Reads OPENAI_API_KEY from config.py (loaded from .env)
#   - services/conversation.py calls generate_summary() after Q5
#     and sends the result back to the candidate on WhatsApp,
#     then saves it to MongoDB via candidates.py
# ---------------------------------------------------------------

from openai import OpenAI
import config

# Create the OpenAI client once, using the key from .env (via config).
client = OpenAI(api_key=config.OPENAI_API_KEY)


def generate_summary(candidate):
    """
    Build a short professional CV summary from a candidate's answers.

    candidate: the record dict from MongoDB, containing full_name,
               qualification, main_skill, years_experience, etc.

    Returns: a 2-3 sentence summary as a plain string.
    """

    # Build a plain-language prompt from the five answers. We pull
    # each field with .get() so a missing value can't crash the call.
    prompt = (
        "Write a short, professional CV summary (2-3 sentences) for a "
        "job seeker, using the details below. Write in the third person. "
        "Keep it simple and positive. Do not invent qualifications.\n\n"
        f"Full name: {candidate.get('full_name', '')}\n"
        f"Highest qualification: {candidate.get('qualification', '')}\n"
        f"Main skill: {candidate.get('main_skill', '')}\n"
        f"Years of experience: {candidate.get('years_experience', '')}\n"
    )

    # Call the OpenAI chat API once. gpt-4o-mini is cheap, fast, and
    # more than good enough for a short summary — right choice for a
    # hackathon demo.
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You write concise, professional CV summaries."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,      # a short summary never needs more
        temperature=0.7,     # a little variety, still grounded
    )

    # Pull the text out of the response and strip whitespace.
    summary = response.choices[0].message.content.strip()
    return summary