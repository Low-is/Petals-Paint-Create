# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Allow requests from your GitHub Pages domain ONLY
CORS(app, origins=["https://yourusername.github.io"])

# Load email credentials and SMTP config
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ORGANIZER_EMAIL = os.getenv('ORGANIZER_EMAIL')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 465))

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

@app.route('/api/rsvp', methods=['POST'])
def rsvp():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    guests = data.get('guests', '0')
    attendance = data.get('attendance')

    if not name or not email or not attendance:
        return jsonify({"error": "Missing required fields"}), 400

    user_subject = "RSVP Confirmation"
    user_body = f"Hi {name},\n\nThank you for your RSVP.\nAttendance: {attendance}\nNumber of guests: {guests}\n\nLooking forward to seeing you at the event!"

    organizer_subject = "New RSVP Received"
    organizer_body = (f"New RSVP Details:\n"
                      f"Name: {name}\n"
                      f"Email: {email}\n"
                      f"Attendance: {attendance}\n"
                      f"Number of guests: {guests}")

    user_email_sent = send_email(email, user_subject, user_body)
    organizer_email_sent = send_email(ORGANIZER_EMAIL, organizer_subject, organizer_body)

    if user_email_sent and organizer_email_sent:
        return jsonify({"message": "RSVP received and confirmation emails sent!"}), 200
    else:
        return jsonify({"error": "Failed to send confirmation emails."}), 500

if __name__ == '__main__':
    app.run()
