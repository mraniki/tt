import asyncio
import logging
from tt.config import settings
from tt.utils import listener, notify, BasePlugin
from talkytrend import TalkyTrend

class TalkyTrendPlugin(BasePlugin):
    def __init__(self):
        self.logger = logging.getLogger(name="TalkyTrend")
        self.talky_trend = None
        self.enabled = settings.talkytrend_enabled

    async def start(self):
        if not self.enabled:
            return

        self.logger.info("Starting TalkyTrend service...")
        self.talky_trend = TalkyTrend()
        asyncio.create_task(self.scanner())

    async def stop(self):
        if not self.enabled:
            return

        self.logger.info("Stopping TalkyTrend service...")

    async def scanner(self):
        while True:
            if not self.enabled:
                await asyncio.sleep(settings.scanner_frequency)
                continue

            messages = await self.talky_trend.check_signal()
            if messages:
                for message in messages:
                    self.logger.info(message)
            event = await self.talky_trend.fetch_key_events()
            if event:
                self.logger.info(f"Key event: {event}")
            news = await self.talky_trend.fetch_key_news()
            if news:
                self.logger.info(f"Key news: {news['title']}")
            await asyncio.sleep(settings.scanner_frequency)
