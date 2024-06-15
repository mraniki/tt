import time

import feedparser
import schedule

from tt.config import logger, settings
from tt.plugins.plugin_manager import BasePlugin
from tt.utils import send_notification


class FeedPlugin(BasePlugin):
    """ """

    def __init__(self):
        """Plugin Initialization"""
        super().__init__()
        self.enabled = settings.rss_feed_plugin_enabled
        self.rss_feed_url = settings.rss_feed_url
        self.rss_feed_frequency = settings.rss_feed_frequency
        if self.enabled:
            logger.debug("RSS feed plugin enabled")

    async def start(self):
        """Starts the plugin"""
        if self.enabled:
            logger.debug("RSS feed plugin started")
            schedule.every(self.rss_feed_frequency).minutes.do(self.poll_rss_feed)
            while True:
                schedule.run_pending()
                time.sleep(1)

    async def send_notification(self, message):
        """Sends a notification"""
        if self.enabled:
            await send_notification(message)

    async def handle_message(self, msg):
        """
        Handles incoming messages.

        Args:
            msg (str): The incoming message.
        """
        if not self.should_handle(msg):
            return

    def poll_rss_feed(self):
        """
        A function that polls the RSS feed,
        retrieves updates from the feed entries,
        and logs the updates.
        """
        feed = feedparser.parse(self.rss_feed_url)

        for entry in feed.entries:
            updates = f"{entry.title} - {entry.link}"
            logger.debug("Updates: {}", updates)
            return updates
