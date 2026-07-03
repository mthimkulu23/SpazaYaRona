# ---------------------------------------------------------------
# backend/app.py
# WHY THIS FILE EXISTS:
#   This is the entry point of the whole backend. Running this file
#   starts the Flask web server that:
#     - the React employer portal calls (to create/view/publish jobs)
#     - Meta's WhatsApp servers call (to deliver incoming messages)
#
# WHAT IT DOES:
#   - Creates the Flask app
#   - Enables CORS so React (port 5173) can call Flask (port 5000)
#   - Checks that all required .env values are present at startup
#   - Registers the route files (webhook + jobs) — added as we build them
#
# HOW IT CONNECTS TO THE REST OF THE PROJECT:
#   - config.py: check_config() runs here so a missing key fails
#     loudly at startup, not mid-demo
#   - routes/webhook.py and routes/jobs.py will be registered here
#     once we build them (commented out for now so this runs today)
# ---------------------------------------------------------------

from flask import Flask
from flask_cors import CORS

import config

# Create the Flask application.
app = Flask(__name__)

# Enable CORS. Without this, the browser blocks React (running on
# http://localhost:5173) from calling Flask (http://localhost:5000)
# because they are different origins. For a hackathon we allow all
# origins — simplest thing that works.
CORS(app)

# Fail loudly at startup if any required .env value is missing.
config.check_config()


# A simple health-check route so we can confirm the server is up
# by visiting http://localhost:5000/ in a browser.
@app.route("/")
def home():
    return {"status": "ok", "message": "WhatsApp CV Builder backend is running"}




from routes.jobs import jobs_bp
app.register_blueprint(jobs_bp)

# ---------------------------------------------------------------
# Route files will be registered here as we build them:
#
#from routes.webhook import webhook_bp
#from routes.jobs import jobs_bp
# app.register_blueprint(webhook_bp)
# app.register_blueprint(jobs_bp)
#
# They are commented out for now so the app runs before those
# files exist. We uncomment each one when we build it.
# ---------------------------------------------------------------


# Run the server. debug=True auto-reloads on code changes and shows
# errors in the browser — helpful during a hackathon. port=5000 is
# the address React and Meta will point to.
if __name__ == "__main__":
    app.run(debug=True, port=5000)