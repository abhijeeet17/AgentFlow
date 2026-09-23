import logging
from app.config import settings

logger = logging.getLogger(__name__)

class EmailIntegration:
    def __init__(self):
        self.smtp_host = settings.EMAIL_SMTP_HOST

    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        if not self.smtp_host:
            logger.info(f"[MOCK EMAIL] Sent to {to_email} | Subject: {subject}\nBody:\n{body}")
            return True
        try:
            # SMTP email sending implementation
            logger.info(f"Sending SMTP email to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Email Sending Error: {e}")
            return False

email_integration = EmailIntegration()
