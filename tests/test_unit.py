"""
 TT test
"""
from unittest.mock import AsyncMock, patch
import pytest

from dxsp import DexSwap
from iamlistening import Listener
from findmyorder import FindMyOrder

import sys
sys.path.append("./src")
from src.config import settings, logger

from src.bot import (
    load_exchange, parse_message,
    execute_order, trading_switch_command,
    init_message, post_init, notify,
    get_account, get_name, get_host_ip, get_ping,
    get_quote, get_trading_asset_balance,
    get_account_position, get_account_balance,
    get_account_margin,
    restart_command,
)

@pytest.fixture
def mock_listener():
    """Fixture to create an listener object for testing."""
    with patch("config.settings", autospec=True):
        settings.discord_webhook_id = "12345678901"
        settings.discord_webhook_token = "1234567890"
        settings.matrix_hostname = None
        settings.telethon_api_id = None
        settings.bot_token = "test_bot_token"
        settings.bot_channel_id = "1234567890"
        settings.bot_msg_help = "this is help"
        return Listener()

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
async def test_parse_message(command_message):
    """Test that the parse_message function returns a non-None value."""
    notify_mock = AsyncMock()
    with patch('src.bot.notify', notify_mock):
        output = await parse_message(command_message)
        assert output is not None, "The output should not be None"


@pytest.mark.asyncio
async def test_notify():
    """Test that the notify function returns a non-None value."""
    notify_mock = AsyncMock()
    with patch('src.bot.notify', notify_mock):
        output = await notify("test")
        assert output is not None, "The output should not be None"

@pytest.mark.asyncio
async def test_get_host_ip():
    """Test that the get_host_ip function returns a non-None value."""
    output = await get_host_ip()
    assert output is not None, "The output should not be None"


@pytest.mark.asyncio
async def test_def_get_ping():
    """Test that the get_ping function returns a non-None value."""
    output = await get_ping()
    assert output is not None, "The output should not be None"


@pytest.mark.asyncio
async def test_load_exchange():
    """Fixture to create an exchange object for testing."""
    with patch("config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_rpc = "https://eth.llamarpc.com"
        settings.dex_chain_id = 1
        settings.cex_name = ""
        loaded_exchange = await load_exchange()
        print(load_exchange)
        assert loaded_exchange is not None


@pytest.mark.asyncio
async def test_execute_order():
    """Test that the execute_order function returns a non-None value."""
    with patch("config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_rpc = "https://eth.llamarpc.com"
        settings.dex_chain_id = 1
        settings.cex_name = ""
        output = await execute_order(order_message)
        print(output)
        assert output is not None


@pytest.mark.asyncio
async def test_get_quote():
    """Test that the get_quote function returns a non-None value."""
    with patch("config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_rpc = "https://eth.llamarpc.com"
        settings.dex_chain_id = 1
        settings.cex_name = ""
        output = await get_quote("WBTC")
        print(output)
        assert output is not None


@pytest.mark.asyncio
async def test_get_name():
    """Test that the get_name function returns a non-None value."""
    with patch("config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_rpc = "https://eth.llamarpc.com"
        settings.dex_chain_id = 1
        settings.cex_name = ""
        output = await get_name()
        print(output)
        assert output is not None


@pytest.mark.asyncio
async def test_get_account():
    """Test that the get_account function returns a non-None value."""
    with patch("config.settings", autospec=True):
        exchange = DexSwap()
        output = await get_account(exchange)
        print(output)
        assert output is not None


@pytest.mark.asyncio
async def test_get_account_balance():
    """Test that the get_account_balance function returns a non-None value."""
    with patch("config.settings", autospec=True):
        exchange = DexSwap()
        output = await get_account_balance()
        print(output)
        assert output is not None


@pytest.mark.asyncio
async def test_get_trading_asset_balance():
    """Test that the get_asset_trading_balance function returns a non-None value."""
    with patch("config.settings", autospec=True):
        exchange = DexSwap()
        output = await get_trading_asset_balance()
        print(output)
        assert output is not None

@pytest.mark.asyncio
async def test_get_account_position():
    """Test that the get_account_positions function returns a non-None value."""
    with patch("config.settings", autospec=True):
        exchange = DexSwap()
        output = await get_account_position()
        print(output)
        assert output is not None

@pytest.mark.asyncio
async def test_get_account_margin():
    """Test that the get_account_margin function returns a non-None value."""
    with patch("config.settings", autospec=True):
        exchange = DexSwap()
        output = await get_account_margin()
        print(output)
        assert output is not None


@pytest.mark.asyncio
async def test_init_message():
    """Test that the init_message function returns a non-None value."""
    with patch("config.settings", autospec=True):
        output = await init_message()
        print(output)
        assert output is not None


@pytest.mark.asyncio
async def test_toggle_trading_active():
    with patch("config.settings", autospec=True):
        print(settings.trading_enabled)
        await trading_switch_command()
        print(settings.trading_enabled)
        assert settings.trading_enabled is False


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
