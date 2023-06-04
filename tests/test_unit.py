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
    return DexSwap()

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
async def test_listener():
    with patch("config.settings", autospec=True):
        settings.discord_webhook_id = "test_discord_webhook_id"
        settings.discord_webhook_token = "1234567890"
        settings.matrix_hostname = None
        settings.telethon_api_id = None
        settings.bot_token = "test_bot_token"
        settings.bot_channel_id = "1234567890"
        settings.bot_msg_help = "this is help"
        listener = Listener()
        print(listener)
        assert listener is not None

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
    """
    Test that the parse_message function returns a non-None value.
    """
    command_message = '/help'
    notify_mock = AsyncMock()
    with patch('src.bot.notify', notify_mock):
        output = await parse_message(command_message)
        assert output is not None, "The output should not be None"



@pytest.mark.asyncio
async def test_load_exchange():
    with patch("config.settings", autospec=True):
        settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
        settings.dex_private_key = "0xdeadbeet"
        settings.dex_rpc = "https://eth.llamarpc.com"
        settings.dex_chain_id = 1
        settings.cex_name = ""
        loaded_exchange = await load_exchange()
        print(loaded_exchange)
        if loaded_exchange:
            assert loaded_exchange is not None


@pytest.mark.asyncio
async def test_toggle_trading_active():
    with patch("config.settings", autospec=True):
        print(settings.trading_enabled)
        await trading_switch_command()
        print(settings.trading_enabled)
        assert settings.trading_enabled is False


# @pytest.mark.asyncio
# async def test_get_name():
#     with patch("config.settings", autospec=True):
#         settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
#         settings.dex_private_key = "0xdeadbeet"
#         settings.dex_rpc = "https://eth.llamarpc.com"
#         settings.dex_chain_id = 1
#         settings.cex_name = ""
#         loaded_exchange = await load_exchange()
#         print(loaded_exchange)
#         name = await get_name()
#         print(name)
#         assert name is not None


# @pytest.mark.asyncio
# async def test_get_account():
#     with patch("config.settings", autospec=True):
#         settings.dex_wallet_address = "0x1234567890123456789012345678901234567899"
#         settings.dex_private_key = "0xdeadbeet"
#         settings.dex_rpc = "https://eth.llamarpc.com"
#         settings.dex_chain_id = 1
#         settings.cex_name = ""
#         loaded_exchange = await load_exchange()
#         print(loaded_exchange)
#         account = await get_account(loaded_exchange)
#         print(account)
#         assert account is not None


# @pytest.mark.asyncio
# async def test_execute_order():
#     # Test case when both action and instrument are not None
#     order_params = {'action': 'buy', 'instrument': 'BTCUSDT'}
#     assert await execute_order(order_params) is None