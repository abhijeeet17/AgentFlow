import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class SlackIntegration:
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or settings.SLACK_WEBHOOK_URL

    async def send_notification(self, message: str) -> bool:
        if not self.webhook_url:
            logger.info(f"[MOCK SLACK] Notification: {message}")
            return True
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json={"text": message})
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"Slack Notification Error: {e}")
            return False

slack_integration = SlackIntegration()
