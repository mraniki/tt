"""
Version Related Utils

"""

__version__ = "8.2.4"


import aiohttp

from tt.config import logger, settings


async def check_version():
    """
    Asynchronously checks the version
    of the GitHub repository.

    This function sends a HEAD request to the
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
            async with session.head(settings.repo, timeout=5) as response:
                if response.status != 200:
                    return

                latest_version = response.headers["X-GitHub-Tag-Name"]
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
