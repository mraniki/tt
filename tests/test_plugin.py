import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from tt.utils import MessageProcessor, start_plugins
from tt.config import settings, logger
from tt.plugins.example_plugin import ExamplePlugin

@pytest.fixture
def message_processor():
    return MessageProcessor()

@pytest.fixture(name="mock_settings_dex")
def mock_settings_dex_fixture():
    class Settings:
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_rpc = "https://eth.llamarpc.com"
        settings.dex_chain_id = 1
        settings.cex_name = ""
        settings.trading_enabled = True
    return Settings()

@pytest.fixture(name="mock_discord")
def mock_discord_fixture():
    """Fixture to create an listener object for testing."""
    class Settings:
        settings.discord_webhook_id = "12345678901"
        settings.discord_webhook_token = "1234567890"
        settings.bot_token = "test_bot_token"
        settings.bot_channel_id = "1234567890"
        settings.ping = "8.8.8.8"
    return Settings()

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



@pytest.fixture
def example_plugin_enabled():
    settings.example_plugin_enabled = True
    yield
    settings.example_plugin_enabled = False

@pytest.mark.asyncio
async def test_example_plugin(example_plugin_enabled):
    # Arrange
    plugin = ExamplePlugin()

    # Act
    await plugin.start()
    await plugin.handle_message(f"{settings.bot_prefix}{settings.bot_command_help}")
    await plugin.handle_message(f"{settings.bot_prefix}{settings.plugin_menu}")
    await plugin.stop()

    # Assert
    assert plugin.should_handle("any message") is True


# @pytest.mark.asyncio
# async def test_parse_command_plugin(mock_settings_dex):
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



@pytest.fixture(name="plugin_enabled")
def plugin_enabled():
    with patch("tt.config.settings", autospec=True):
        settings.plugin_enabled = True
        return settings

@pytest.fixture
def mock_start_plugins():
    return AsyncMock()

# @pytest.fixture
# async def test_listener(plugin_enabled):
#     bot_listener = Listener()
#     task = asyncio.create_task(bot_listener.run_forever())
#     message_processor = MessageProcessor()
#     if settings.plugin_enabled:
#         message_processor.load_plugins("tt.plugins")
#         loop = asyncio.get_running_loop()
#         loop.create_task(start_plugins(message_processor))
#     task = asyncio.create_task(bot_listener.run_forever())

#     yield bot_listener

#     await bot_listener.stop()
#     task.cancel()

# @pytest.fixture
# def message_processor():
#     return MessageProcessor()