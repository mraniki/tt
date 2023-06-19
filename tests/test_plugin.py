import pytest
import asyncio
import re
from unittest.mock import AsyncMock, MagicMock, patch
from tt.utils import MessageProcessor, start_plugins
from tt.config import settings, logger
from tt.plugins.example_plugin import ExamplePlugin

@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")

@pytest.fixture
def message_processor():
    return MessageProcessor()


@pytest.fixture
def mock_start_plugins():
    return AsyncMock()


@pytest.mark.asyncio
async def test_load_plugins():
    message_processor = MessageProcessor()
    message_processor.load_plugins("tt.plugins")
    print("Loaded plugins:", message_processor.plugins)
    assert len(message_processor.plugins) >= 1


@pytest.mark.asyncio
async def test_start_plugins():
    message_processor = MessageProcessor()
    message_processor.load_plugins("tt.plugins")
    loop = asyncio.get_running_loop()
    loop.create_task(start_plugins(message_processor))
    assert len(message_processor.plugins) >= 1


@pytest.mark.asyncio
async def test_example_plugin():
    # Arrange
    plugin = ExamplePlugin()

    # Act
    await plugin.start()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    await plugin.handle_message(f"{settings.bot_prefix}{settings.plugin_menu}")
    await plugin.stop()
    assert plugin.should_handle("any message") is True


@pytest.mark.asyncio
async def test_exception_example_plugin():
    plugin = ExamplePlugin()
    with pytest.raises(
        Exception, 
        match=re.escape(
            "ExamplePlugin.start() takes 1 positional argument but 2 were given")):
        await plugin.start("any message")


# @pytest.mark.asyncio
# async def test_handle_message_plugin(mock_settings_dex):
#     """Test parse_message balance """
#     send_notification_mock = AsyncMock()
#     with patch('tt.utils.send_notification',send_notification_mock):
#         message_processor = MessageProcessor()
#     # if settings.plugin_enabled:
#         message_processor.load_plugins("tt.plugins")
#         loop = asyncio.get_running_loop()
#         await loop.create_task(start_plugins(message_processor))
#         await message_processor.process_message('/plugin')
#         assert '⚙️' in send_notification_mock.call_args[0][0]
