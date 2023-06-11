import asyncio
import logging
from tt.config import settings
from talkytrend import TalkyTrend
from tt.config import PluginManager, BasePlugin

class TalkyTrendPlugin(BasePlugin):
    def __init__(self):
        self.talky_trend = None
        self.logger = None

    async def start(self):
        self.logger = logging.getLogger(name="TalkyTrend")
        self.logger.info("Starting TalkyTrend service...")
        self.talky_trend = TalkyTrend()
        asyncio.create_task(self.scanner())

    async def stop(self):
        self.logger.info("Stopping TalkyTrend service...")

    async def scanner(self):
        while True:
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

# Register the plugin with the PluginManager
PluginManager.register_plugin(TalkyTrendPlugin)