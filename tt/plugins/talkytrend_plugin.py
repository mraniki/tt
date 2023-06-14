from tt.utils import notify, listener, BasePlugin
from tt.config import logger
from talkytrend import TalkyTrend

class TalkyTrendPlugin(BasePlugin):
    def __init__(self):
        try:
            self.trend = TalkyTrend()
            logger.debug("plugin init TalkyTrend")
        except Exception as e:
            logger.warning("talkytrend init %s",e)
    async def start(self):
        """Starts the TalkyTrend plugin"""
        logger.debug("talkytrend start TalkyTrend")
        try:
            while True:
                async for message in self.trend.scanner():
                    await self.notify(message)
        except Exception as e:
            logger.warning("talkytrend start %s",e)

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
        try:
            await notify(message)
        except Exception as e:
            logger.warning("talkytrend notify %s",e)
