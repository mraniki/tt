"""
 talky Utils
"""
__version__ = "6.6.0"


import asyncio

import aiohttp
from apprise import Apprise, NotifyFormat
from iamlistening import Listener

from tt.config import logger, settings
from tt.plugins.plugin_manager import PluginManager


async def send_notification(msg):
    """
    💬 Notification via Apprise.
    Apprise endpoint URL can be a URL
    for the chat, a URL to an Apprise config
    or a URL to the Apprise API endpoint
    apprise_url = "tgram://BOTTOKEN/CHANNEL"
    apprise_url = "discord://token1/channel"

    Args:
        msg (str): Message

    Returns:
        None

    More info
    https://github.com/caronc/apprise/wiki

    """
    aobj = Apprise(settings.apprise_url)
    msg_format = settings.apprise_format or NotifyFormat.MARKDOWN
    try:
        await aobj.async_notify(body=msg, body_format=msg_format)
    except Exception as error:
        logger.error("Verify Apprise URL: ", error)


async def run_bot():
    """
    🤖 Run the chat bot & the plugins
    via an asyncio loop.

    Returns:
        None

    More info: https://github.com/mraniki/iamlistening

    """
    if settings.version_check:
        await check_version()
    listener = Listener()
    plugin_manager = PluginManager()
    await asyncio.gather(start_bot(listener, plugin_manager))


async def start_plugins(plugin_manager):
    """
    🔌 Start all plugins.


    Returns:
        None

    Refer to chat manager for plugin info

    """
    if settings.plugin_enabled:
        plugin_manager.load_plugins(settings.authorized_plugins)
        loop = asyncio.get_running_loop()
        loop.create_task(plugin_manager.start_all_plugins())


async def start_bot(listener, plugin_manager, max_iterations=None):
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
    await start_plugins(plugin_manager)
    iteration = 0
    while True:
        for client in listener.clients:
            msg = await client.get_latest_message()
            if msg:
                await plugin_manager.process_message(msg)
        iteration += 1
        if max_iterations is not None and iteration >= max_iterations:
            break

    await asyncio.sleep(1)


async def check_version():
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
            async with session.get(settings.repo, timeout=10) as response:
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
