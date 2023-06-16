"""
 TT test
"""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import sys
sys.path.insert(0,"..")

from iamlistening import Listener
from fastapi.testclient import TestClient
from tt.bot import app
from tt.utils import (
    parse_message, send_notification,
    get_host_ip, get_ping,
    load_exchange, execute_order,
    get_name, get_quote, get_trading_asset_balance,
    get_account, get_account_balance, 
    get_account_position,get_account_margin,
    trading_switch_command,
    # restart_command,
    init_message, post_init)
from tt.config import settings, logger

@pytest.fixture(name="mock_settings_cex")
def mock_settings_cex_fixture():
    class Settings:
        cex_name = 'binance'
        cex_api = 'api_key'
        cex_secret = 'secret_key'
        cex_password = 'password'
        cex_defaulttype = 'spot'
        cex_testmode = False
        dex_chain_id = ''
    return Settings()

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

@pytest.fixture(name="mock_telegram")
def mock_telegram_fixture():
    """Fixture to create an listener object for testing."""
    class Settings:
        settings.telethon_api_id = "123456789"
        settings.telethon_api_hash = "123456789"
        settings.bot_token = "test_bot_token"
        settings.bot_channel_id = "1234567890"
    return Settings()

@pytest.fixture(name="mock_matrix_")
def mock_matrix_fixture():
    """Fixture to create an listener object for testing."""
    class Settings:
        settings.matrix_hostname = "https://matrix.org"
        settings.matrix_user = "@thismock:matrix.org"
        settings.matrix_pass = "1234"
        settings.bot_token = "token_123435"
        settings.bot_channel_id = "1234567890"
    return Settings()

@pytest.fixture(name="message")
def message_fixture():
    return "hello"

@pytest.fixture
def command_message():
    return "/help"

@pytest.fixture
def order_params():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'EURUSD',
        'quantity': 1,
        # other order parameters
    }


@pytest.mark.asyncio
async def test_parse_help(mock_settings_dex):
    """Test parse_message balance """
    send_notification_mock = AsyncMock()
    with patch('tt.utils.send_notification',send_notification_mock):
        await load_exchange()
        await parse_message('/help')
        assert '🏦' in send_notification_mock.call_args[0][0]


# @pytest.mark.asyncio
# async def test_parse_bal(mock_settings_dex):
#     """Test parse_message balance """
#     send_notification_mock = AsyncMock()
#     with patch('tt.utils.send_notification',send_notification_mock):
#         await load_exchange()
#         await parse_message('/bal')
#         assert '🏦' in send_notification_mock.call_args[0][0]


# @pytest.mark.asyncio
# async def test_parse_quote(mock_settings_dex):
#     """Test parse_message balance """
#     send_notification_mock = AsyncMock()
#     with patch('tt.utils.send_notification',send_notification_mock):
#         await load_exchange()
#         await parse_message('/quote WBTC')
#         assert '🦄' in send_notification_mock.call_args[0][0]


@pytest.mark.asyncio
async def test_parse_trading(mock_settings_dex):
    """Test parse_message balance """
    send_notification_mock = AsyncMock()
    with patch('tt.utils.send_notification',send_notification_mock):
        await load_exchange()
        await parse_message('/trading')
        assert 'Trading is' in send_notification_mock.call_args[0][0]


@pytest.mark.asyncio
async def test_send_notification(caplog, mock_discord):
    """Test send_notification function"""
    send_notification_mock = AsyncMock()
    with patch('tt.utils.send_notification',send_notification_mock):

        message = '<code>test message</code>'

        output = await send_notification(message)
        print(output)
        assert 'https://discord.com/api/webhooks/12345678901/1234567890' in caplog.text


@pytest.mark.asyncio
async def test_get_host_ip():
    """Test get_host_ip """
    output = get_host_ip()
    assert output is not None


# @pytest.mark.asyncio
# async def test_def_get_ping(mock_discord):
#     """Test get_ping function """
#     output = get_ping()
#     print(output)
#     assert output is not None


@pytest.mark.asyncio
async def test_dex_load_exchange(mock_settings_dex):
    """test exchange dex"""
    exchange = await load_exchange()
    print(exchange)
    assert exchange is not None


@pytest.mark.asyncio
async def test_cex_load_exchange(mock_settings_cex):
    """test exchange cex"""
    exchange = await load_exchange()
    print(exchange)
    assert exchange is not None


# @pytest.mark.asyncio
# async def test_successful_execute_order(caplog, order_params, mock_settings_dex):
#     await load_exchange()
#     dex_execute_mock = AsyncMock()
#     with patch('dxsp.execute_order',dex_execute_mock):
#         trade_confirmation = await execute_order(order_params)

#         # Assert that no warning is logged
#         assert "execute_order:" not in caplog.text
#         # Assert that no notification is sent
#         assert "⚠️ order execution:" not in caplog.text
#         # Assert that the trade confirmation is returned
#         assert isinstance(trade_confirmation, str)
#         # Add more specific assertions for the trade confirmation if needed
#         assert "⬇️" in trade_confirmation or "⬆️" in trade_confirmation
#         assert "Size:" in trade_confirmation
#         assert "Entry:" in trade_confirmation
#         assert "ℹ️" in trade_confirmation
#         assert "🗓️" in trade_confirmation



@pytest.mark.asyncio
async def test_failed_execute_order(caplog, order_params,mock_settings_dex):
    await load_exchange()
    trade_confirmation = await execute_order(order_params)
    assert 'Order execution failed' in caplog.text


@pytest.mark.asyncio
async def test_get_quote(mock_settings_dex):
    """Test get_quote """
    await load_exchange()
    output = await get_quote("WBTC")
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_name(mock_settings_dex):
    """Test get_name function."""
    await load_exchange()
    output = await get_name()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_account_balance(mock_settings_dex):
    """Test get_account_balance."""
    await load_exchange()
    output = await get_account_balance()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_trading_asset_balance(mock_settings_dex):
    """Test get_asset_trading_balance."""
    await load_exchange()
    output = await get_trading_asset_balance()
    print(output)
    assert output is not None

    
@pytest.mark.asyncio
async def test_get_account_position(mock_settings_dex):
    """Test get_account_positions."""
    await load_exchange() 
    output = await get_account_position()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_account_margin(mock_settings_dex):
    """Test get_account_margin """
    await load_exchange() 
    output = await get_account_margin()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_init_message(mock_settings_dex):
    """Test test_init_message."""
    await load_exchange()
    output = await init_message()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_toggle_trading_active(mock_settings_dex):
    print(settings.trading_enabled)
    await trading_switch_command()
    print(settings.trading_enabled)
    assert settings.trading_enabled is False


@pytest.mark.asyncio
async def test_listener(mock_discord):
    listener = Listener()
    print(listener)
    assert listener is not None


@pytest.mark.asyncio
async def test_message_listener(mock_telegram, message):
    listener = Listener()
    print(listener)
    assert listener is not None
    await listener.handle_message(message)
    msg = await listener.get_latest_message()
    print(msg)
    assert msg == "hello"


def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200

def test_read_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200

def test_webhook_with_valid_payload(mock_discord):
    client = TestClient(app)
    payload = {"key": "my_secret_key", "data": "my_data"}
    response = client.post("/webhook", json=payload)
    assert response is not None
