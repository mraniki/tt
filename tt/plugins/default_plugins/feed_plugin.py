import feedparser

from tt.config import logger, settings
from tt.plugins.plugin_manager import BasePlugin


class FeedPlugin(BasePlugin):
    """ """

    def __init__(self):
        """Plugin Initialization"""
        super().__init__()
        self.enabled = settings.rss_feed_plugin_enabled
        if self.enabled:
            self.rss_feed_url = settings.rss_feed_url
            self.rss_feed_frequency = settings.rss_feed_frequency
            self.rss_prefix = settings.rss_prefix
            logger.debug("RSS feed plugin enabled")

    async def start(self):
        """Starts the plugin"""
        if self.enabled:
            logger.debug("RSS feed plugin started")
            await self.plugin_notify_schedule_task(
                user_name="talky_feed",
                frequency=self.rss_feed_frequency,
                frequency_unit="minutes",
                function=self.poll_rss_feed,
            )

    # async def send_notification(self, message):
    #     """Sends a notification"""
    #     if self.enabled:
    #         await self.send_notification(message)

    async def poll_rss_feed(self):
        """
        A function that polls the RSS feed,
        retrieves updates from the feed entries,
        and logs the updates.
        """
        try:
            feed = feedparser.parse(self.rss_feed_url)
            if not feed:
                logger.warning("Failed to parse RSS feed")
                return

            for entry in feed.entries:
                if updates := f"{self.rss_prefix}{entry.title} - {entry.link}":
                    await self.send_notification(updates)
        except Exception as e:
            logger.error("Error polling RSS feed: %s", e)
