from talkytrend import TalkyTrend

from tt.config import settings
from tt.plugins.plugin_manager import BasePlugin


class TalkyTrendPlugin(BasePlugin):

    def __init__(self):
        """
        Initialize the TalkyTrendPlugin class
        by setting the 'enabled' attribute to
        the value of 'settings.talkytrend_enabled'.
        If 'enabled' is True,
        instantiate a TalkyTrend object.
        """
        super().__init__()
        self.enabled = settings.talkytrend_enabled
        self.bot_command_trend = settings.bot_command_trend
        self.bot_command_news = settings.bot_command_news
        self.bot_command_tv = settings.bot_command_tv
        self.bot_command_scraper = settings.bot_command_scraper

        if self.enabled:
            self.trend = TalkyTrend()

    async def start(self):
        """
        Asynchronously starts the plugin if it is enabled.

        This function checks if the plugin is enabled by
        checking the value of the `enabled` attribute.
        If the plugin is enabled, it calls the
        `plugin_notify_cron_task` method with
        the `user_name` parameter set to "talky_monitor"
        and the `function` parameter set to
        the `monitor` method of the `trend` object.

        This function is called when the plugin is started.

        Parameters:
            None

        Returns:
            None
        """
        if self.enabled:
            await self.plugin_notify_cron_task(
                user_name="talky_monitor", function=self.trend.monitor
            )

    async def handle_message(self, msg):
        """
        Handles incoming messages and
        routes them to the appropriate function.

        Args:
            msg (str): The message received by the plugin.

        Returns:
            None: If the message should not be handled.
            None: If the message is a command and
            the corresponding function is executed successfully.
            None: If the message is not a command.

        Supported functions are:

        - `get_talkytrend_info()`
        - `fetch_signal()`
        - `fetch_feed()`
        - `get_tv()`
        - `scrape_page()`

        """

        if self.should_filter(msg):
            return
        elif self.is_command_to_handle(msg):
            command, *args = msg.split(" ")
            command = command[1:]

            command_mapping = {
                self.bot_command_info: self.trend.get_talkytrend_info,
                # self.bot_command_info: self.trend.get_info,
                self.bot_command_trend: self.trend.fetch_signal,
                self.bot_command_news: self.trend.fetch_feed,
                self.bot_command_tv: self.trend.get_tv,
                # self.bot_command_tv: self.trend.fetch_tv,
                self.bot_command_scraper: self.trend.scrape_page,
                # self.bot_command_scraper: self.trend.fetch_page,
            }

            if command in command_mapping:
                function = command_mapping[command]
                await self.send_notification(f"{await function()}")
