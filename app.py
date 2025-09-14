import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Load environment variables from the .env file
load_dotenv()

# Construct the absolute path to the 'static' folder for reliability on production servers
static_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, static_folder=static_folder_path)

# --- Brevo API Configuration ---
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


# --- API Endpoint for the Contact Form ---
@app.route('/api/contact', methods=['POST'])
def handle_contact_form():
    """
    Receives contact form data, sends an email via Brevo's API, and returns a response.
    """
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    subject = data.get('subject', 'No Subject')
    message_body = data.get('message')

    if not all([name, email, message_body]):
        return jsonify({"error": "Missing required fields: name, email, and message."}), 400

    recipient_email = os.getenv('RECIPIENT_EMAIL')
    sender_email = os.getenv('SENDER_EMAIL') # This must be a verified sender in Brevo

    if not all([recipient_email, sender_email, configuration.api_key['api-key']]):
        print("ERROR: Brevo API Key, recipient, or sender email is not set.")
        return jsonify({"error": "Server configuration error."}), 500

    # Construct the email using Brevo's SDK
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[sib_api_v3_sdk.SendSmtpEmailTo(email=recipient_email)],
        reply_to=sib_api_v3_sdk.SendSmtpEmailReplyTo(email=email, name=name),
        sender=sib_api_v3_sdk.SendSmtpEmailSender(name="Nishil's Portfolio", email=sender_email),
        subject=f"New Portfolio Contact from {name}: {subject}",
        html_content=f"""
            <h3>You have a new message from your portfolio:</h3>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <hr>
            <p><strong>Message:</strong></p>
            <p>{message_body.replace(os.linesep, '<br>')}</p>
        """
    )

    try:
        # Send the email
        api_instance.send_transac_email(send_smtp_email)
        return jsonify({"message": "Thank you! Your message has been sent successfully."}), 200

    except ApiException as e:
        print(f"BREVO API EXCEPTION: {e.body}")
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

