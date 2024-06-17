import asyncio

import aiohttp
from iamlistening import Listener

from tt.config import logger, settings
from tt.plugins.plugin_manager import PluginManager
from tt.utils import Notifier, __version__


class Bot:
    def __init__(self):
        logger.info("Initializing bot")

        self.bot = None
        self.version = __version__ or "0.0.0"
        self.name = settings.name or "Talky"
        self.Listener = Listener()
        self.Notifier = Notifier()
        self.PluginManager = PluginManager()

        self.version_check = settings.version_check
        self.repository = settings.repo
        self.plugin_enabled = settings.plugin_enabled
        self.authorized_plugins = settings.authorized_plugins

        logger.info("Bot initialized")

    async def run_bot(self):
        """
        🤖 Run the chat bot & the plugins
        via an asyncio loop.

        Returns:
            None

        More info: https://github.com/mraniki/iamlistening

        """
        if self.version_check:
            await self.check_version()
        await asyncio.gather(self.start_bot(self.listener, self.plugin_manager))

    async def send_notification(self, msg):
        """
        📨 Send a notification

        Args:
            msg (str): Message

        Returns:
            None

        """
        await self.Notifier.notify(msg)

    async def start_plugins(self, plugin_manager):
        """
        🔌 Start all plugins.


        Returns:
            None

        Refer to chat manager for plugin info

        """
        if self.plugin_enabled:
            plugin_manager.load_plugins(self.authorized_plugins)
            loop = asyncio.get_running_loop()
            loop.create_task(plugin_manager.start_all_plugins())

    async def start_bot(self, listener, plugin_manager, max_iterations=None):
        """
        👂 Start the chat listener and
        dispatch messages to plugins

        Args:
            listener (Listener): Listener
            plugin_manager (PluginManager): PluginManager
            max_iterations (int): Max iterations

        Returns:
            None

        """

        loop = asyncio.get_running_loop()
        loop.create_task(listener.start())
        await self.start_plugins(plugin_manager)
        iteration = 0
        if not listener.clients:
            logger.warning(
                """
                No listener clients.
                Verify settings and check wiki for example
                https://talky.readthedocs.io/en/latest/02_config.html
                """
            )
            return
        while True:
            for client in listener.clients:
                msg = await client.get_latest_message()
                if msg:
                    await plugin_manager.process_message(msg)
            iteration += 1
            if max_iterations is not None and iteration >= max_iterations:
                break

        await asyncio.sleep(1)

    async def check_version(self):
        """
        Asynchronously checks the version
        of the GitHub repository.

        This function sends a GET request to the
        specified GitHub repository URL and retrieves the
        latest version of the repository.
        It then compares the latest version
        with the current version (__version__)
        and logs the result.

        Parameters:
            None

        Returns:
            None
        """

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.repository, timeout=10) as response:
                    if response.status != 200:
                        return

                    github_repo = await response.json()
                    latest_version = github_repo["name"]
                    if latest_version != f"v{__version__}":
                        logger.debug(
                            "You are NOT using the latest %s: %s",
                            latest_version,
                            __version__,
                        )
                    else:
                        logger.debug(f"You are using the latest {__version__}")
        except Exception as error:
            logger.error("check_version: {}", error)
