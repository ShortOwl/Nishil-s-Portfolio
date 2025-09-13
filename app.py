import os
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialise the Flask application
static_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, static_folder=static_folder_path)

# --- API Endpoint for the Contact Form ---
@app.route('/api/contact', methods=['POST'])
def handle_contact_form():
    """
    Receives contact form data, sends an email with proper headers, and returns a response.
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject', 'No Subject')
    message = data.get('message')

    if not all([name, email, message]):
        return jsonify({"error": "Missing required fields: name, email, and message."}), 400

    sender_email = os.getenv('SENDER_EMAIL')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_login = os.getenv('SMTP_LOGIN')
    smtp_password = os.getenv('SMTP_PASSWORD')

    if not all([sender_email, recipient_email, smtp_host, smtp_port, smtp_login, smtp_password]):
        print("ERROR: Email credentials are not set in the .env file.")
        return jsonify({"error": "Server configuration error."}), 500

    try:
        # Construct the email
        msg = EmailMessage()
        msg['Subject'] = f"New Portfolio Contact from {name}: {subject}"
        msg['From'] = f"Nishil's Portfolio <{sender_email}>"
        msg['To'] = recipient_email
        msg['Reply-To'] = email

        email_body = (
            f"You have a new message from your portfolio website:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"Message:\n{message}"
        )
        msg.set_content(email_body)

        # Connect to Brevo SMTP and send
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_login, smtp_password)
            server.send_message(msg)

        return jsonify({"message": "Thank you! Your message has been sent successfully."}), 200

    except Exception as e:
        print(f"EMAIL SENDING FAILED: {e}")
        return jsonify({"error": "Sorry, there was a problem sending your message. Please try again later."}), 500


# --- Route to Serve the Frontend ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
