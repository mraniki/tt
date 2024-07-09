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

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await self.send_notification(message)

    def poll_rss_feed(self):
        """
        A function that polls the RSS feed,
        retrieves updates from the feed entries,
        and logs the updates.
        """
        feed = feedparser.parse(self.rss_feed_url)
        # logger.debug("Feed: {}", feed)
        for entry in feed.entries:
            updates = f"{entry.title} - {entry.link}"
            logger.debug("Updates: {}", updates)
            return await self.send_notification(updates)
