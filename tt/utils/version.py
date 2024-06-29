"""
Version Related Utils

"""

__version__ = "9.3.4"


import aiohttp

from tt.config import logger, settings


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
