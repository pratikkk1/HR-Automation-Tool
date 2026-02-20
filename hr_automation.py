import imaplib
import email
import re
import os
import smtplib
from email.mime.text import MIMEText
from PyPDF2 import PdfReader
from twilio.rest import Client

# ================== CONFIG ==================

EMAIL_ID = "pm*******@gmail.com"
EMAIL_PASSWORD = "****************"

HR_EMAIL = "pm********@gmail.com"

TWILIO_SID = "******************"
TWILIO_AUTH = "*******************"
TWILIO_WHATSAPP = "whatsapp:+14*******"   # Twilio sandbox number
YOUR_WHATSAPP = "whatsapp:+91-73*******"   # Your WhatsApp number

REQUIRED_SKILLS = ["react", "python", "sql"]
SKILL_MATCH_THRESHOLD = 100   # percentage

DOWNLOAD_FOLDER = "resumes"

# ============================================

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


# ------------------ EMAIL READER ------------------

def connect_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_ID, EMAIL_PASSWORD)
    mail.select("inbox")
    return mail


# ------------------ PHONE CHECK ------------------

def extract_phone(text):
    match = re.search(r"\b[6-9]\d{9}\b", text)
    return match.group() if match else None


# ------------------ PDF TEXT EXTRACT ------------------

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()


# ------------------ SKILL MATCHING ------------------

def skill_match(text):

    matched = []

    for skill in REQUIRED_SKILLS:
        if skill.lower() in text:
            matched.append(skill)

    percentage = (len(matched) / len(REQUIRED_SKILLS)) * 100

    return percentage, matched


# ------------------ SEND EMAIL ------------------

def send_email_reply(to_email, message):

    msg = MIMEText(message)
    msg["Subject"] = "Job Application "
    msg["From"] = EMAIL_ID
    msg["To"] = to_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL_ID, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()


# ------------------ SEND WHATSAPP ------------------

def send_whatsapp(msg):

    client = Client(TWILIO_SID, TWILIO_AUTH)

    client.messages.create(
        body=msg,
        from_=TWILIO_WHATSAPP,
        to=YOUR_WHATSAPP
    )


# ------------------ MAIN LOGIC ------------------

def process_emails():

    mail = connect_mail()

    #status, messages = mail.search(None, 'UNSEEN')
    status, messages = mail.search(None, 'ALL')

    mail_ids = messages[0].split()[::-1]
    #mail_ids = mail_ids[:1]


    print("Total New Emails:", len(mail_ids))

    for mail_id in mail_ids:

        status, msg_data = mail.fetch(mail_id, '(RFC822)')

        for response_part in msg_data:

            if isinstance(response_part, tuple):

                msg = email.message_from_bytes(response_part[1])

                sender = msg["from"]
                subject = msg["subject"]

                print("\nProcessing:", subject)

                body = ""
                resume_path = None

                # --------- Read Body + Attachment ---------

                if msg.is_multipart():

                    for part in msg.walk():

                        content_type = part.get_content_type()

                        if content_type == "text/plain":
                            body = part.get_payload(decode=True).decode()

                        if part.get_filename():
                            filename = part.get_filename()

                            if filename.lower().endswith(".pdf"):

                                filepath = os.path.join(DOWNLOAD_FOLDER, filename)

                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))

                                resume_path = filepath

                else:
                    body = msg.get_payload(decode=True).decode()

                full_text = body.lower()

                # --------- PHONE CHECK ---------

                phone = extract_phone(full_text)

                if not phone:
                    #send_email_reply(sender, "Phone number missing. Please include your contact number.")
                    #print("Rejected: Phone Missing")
                    continue

                # --------- PDF CHECK ---------

                if not resume_path:
                    send_email_reply(sender, "Resume PDF missing. Please attach your resume.")
                    print("Rejected: Resume Missing")
                    continue

                # --------- SKILL MATCH ---------

                resume_text = extract_text_from_pdf(resume_path)

                combined_text = full_text + resume_text

                match_percent, matched_skills = skill_match(combined_text)

                print("Skill Match:", match_percent)
                

                # --------- FINAL DECISION ---------

                if match_percent >= SKILL_MATCH_THRESHOLD:

                    message = f"""
New Job Application Approved

Email: {sender}
Phone: {phone}
Skill Match: {match_percent}%
Matched Skills: {matched_skills}
"""

                    send_whatsapp(message)

                    send_email_reply(sender, "Your application has been received successfully.")

                    print("Application Approved")

                else:

                    send_email_reply(sender, "Your skills do not match the requirements for this position.")

                    print("Application Rejected (Skill Mismatch)")

    mail.logout()


# ------------------ RUN ------------------

if __name__ == "__main__":
    process_emails()






