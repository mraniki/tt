from time import sleep
from unittest.mock import AsyncMock

import pytest

from tt.config import settings
from tt.plugins.default_plugins.feed_plugin import FeedPlugin


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")


@pytest.fixture(name="plugin")
def test_fixture_plugin():
    return FeedPlugin()


@pytest.mark.asyncio
async def test_plugin(plugin):
    """Test message handling"""

    assert callable(plugin.plugin_notify_schedule_task)


@pytest.mark.asyncio
async def test_plugin_poll_rss_feed(plugin):
    """Test notification"""
    plugin.poll_rss_feed = AsyncMock()
    sleep(60)
    plugin.poll_rss_feed.assert_awaited_once
