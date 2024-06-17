import apprise
from apprise import NotifyFormat

from tt.config import logger, settings


class Notifier:
    """
    💬 Notification via Apprise.

    """

    def __init__(self):
        logger.debug("Notifier initialized")

        self.msg_format = settings.apprise_format or NotifyFormat.MARKDOWN
        self.apprise_url = settings.apprise_url

        self.aobj = apprise.Apprise(settings.apprise_url)

    async def notify(self, msg):
        await self.aobj.async_notify(body=msg, body_format=self.msg_format)
