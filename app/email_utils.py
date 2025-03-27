import logging
import smtplib
from email.mime.text import MIMEText
from .config import (
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS,
    ALERT_EMAIL_FROM, ALERT_EMAIL_TO
)

logger = logging.getLogger(__name__)

def send_alert_email(clinician_id: int):
    subject = f"Clinician {clinician_id} Out of Zone"
    body = f"Clinician with ID {clinician_id} is out of the expected zone."
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL_FROM
    msg["To"] = ALERT_EMAIL_TO

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logger.info(f"Alert email sent for clinician {clinician_id}")
    except Exception as e:
        logger.error(f"Error sending email for clinician {clinician_id}: {e}")
