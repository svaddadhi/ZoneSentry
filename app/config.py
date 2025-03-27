import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test")
CLINICIAN_IDS = [int(id) for id in os.getenv("CLINICIAN_IDS", "1,2,3,4,5,6").split(",")]

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "120"))  # Poll every 2 minutes

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", "")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "")
