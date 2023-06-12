from tt.config import settings
from tt.utils import notify, BasePlugin
from talkytrend import TalkyTrend

class TalkyTrendPlugin(BasePlugin):
    def __init__(self):
        self.trend = TalkyTrend()

    async def start(self):
        """Starts the TalkyTrend plugin"""
        while True:
            async for message in self.trend.scanner():
                await self.notify(message)

    async def stop(self):
        """Stops the TalkyTrend plugin"""
        # Perform any necessary cleanup or shutdown tasks
        pass

    async def listen(self, message):
        """Listens for incoming messages or events"""
        # This plugin doesn't require listening for messages or events
        pass

    async def notify(self, message):
        """Sends a notification"""
        await notify(message)