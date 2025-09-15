import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Construct static folder path
static_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, static_folder=static_folder_path)
CORS(app)

# Resend config
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")  # default to sandbox
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# --- Contact Form API ---
@app.route("/api/contact", methods=["POST"])
def handle_contact_form():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        message = data.get("message")
        subject = data.get("subject", "New Contact Form Message")

        if not name or not email or not message:
            return jsonify({"error": "All fields are required"}), 400

        body = f"""
        You have a new portfolio message:

        Name: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message}
        """

        # Send email via Resend
        response = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": SENDER_EMAIL,
                "to": RECIPIENT_EMAIL,
                "subject": subject,
                "text": body,
                "reply_to": email
            }
        )

        if response.status_code == 200:
            return jsonify({"message": "Thank you! Your message has been sent successfully."}), 200
        else:
            print("Resend error:", response.text)   # 👈 log the actual error
            return jsonify({"error": "Failed to send message", "details": response.json()}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Frontend routes ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
