"""
 TT test
"""
from unittest.mock import AsyncMock, patch
import pytest

from dxsp import DexSwap
from iamlistening import Listener
from findmyorder import FindMyOrder

from src.bot import (
    load_exchange, parse_message, 
    init_message, post_init, notify,
    execute_order, trading_switch_command,
    get_account, get_name, get_host_ip, get_ping,
    get_quote, get_trading_asset_balance,
    get_account_position, get_account_balance, 
    get_account_margin,
    restart_command,
)
from src.config import settings, logger



@pytest.fixture
def mock_exchange():
    """Fixture to create an exchange object for testing."""
    with patch("config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_rpc = "https://eth.llamarpc.com"
        settings.dex_chain_id = 1
        settings.cex_name = ""
        loaded_exchange = await load_exchange()
        print(load_exchange)
        return loaded_exchange

@pytest.fixture
def mock_listener():
    """Fixture to create an listener object for testing."""
    with patch("config.settings", autospec=True):
        settings.discord_webhook_id = "test_discord_webhook_id"
        settings.discord_webhook_token = "1234567890"
        settings.matrix_hostname = None
        settings.telethon_api_id = None
        settings.bot_token = "test_bot_token"
        settings.bot_channel_id = "1234567890"
        settings.bot_msg_help = "this is help"
        listener = Listener()
        return listener

@pytest.fixture
def message():
    return "hello"

@pytest.fixture
def command_message():
    return "/help"

@pytest.fixture
def order_message():
    return "buy EURUSD"

@pytest.mark.asyncio
async def test_listener(mock_listener):
    with patch("config.settings", autospec=True):
        print(mock_listener)
        assert mock_listener is not None

@pytest.mark.asyncio
async def test_message_listener(mock_listener, message):
    print(mock_listener)
    assert mock_listener is not None
    await mock_listener.handle_message(message)
    # Call the function to be tested
    msg = await mock_listener.get_latest_message()
    print(msg)
    assert msg == "hello"


@pytest.mark.asyncio
async def test_parse_message():
    """Test that the parse_message function returns a non-None value."""
    command_message = '/help'
    notify_mock = AsyncMock()
    with patch('src.bot.notify', notify_mock):
        output = await parse_message(command_message)
        assert output is not None, "The output should not be None"


@pytest.mark.asyncio
async def test_load_exchange(mock_exchange):
    print(mock_exchange)
    if mock_exchange:
        assert mock_exchange is not None


@pytest.mark.asyncio
async def test_toggle_trading_active():
    with patch("config.settings", autospec=True):
        print(settings.trading_enabled)
        await trading_switch_command()
        print(settings.trading_enabled)
        assert settings.trading_enabled is False


