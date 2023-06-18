"""
 TT test
"""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import ccxt
import dxsp
import iamlistening
from iamlistening import Listener
from fastapi.testclient import TestClient
from tt.bot import app
# from tt.utils import (
#     parse_message,,
#     init_message, get_host_ip, 
#     execute_order, get_name, get_quote,
#     get_trading_asset_balance, get_account,
#     get_account_balance, get_account_position,
#     get_account_margin,
#     )
from tt.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing")

@pytest.fixture(name="settings_cex")
def set_test_settings_CEX():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing_cex")

@pytest.fixture(name="settings_dex_56")
def set_test_settings_DEX56():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing_dex_56")

@pytest.fixture(name="settings_dex_10")
def set_test_settings_DEX10():
    settings.configure(FORCE_ENV_FOR_DYNACONF="testing_dex_10")

def test_dynaconf_is_in_testing_env_CEX(settings_cex):
    print(settings.VALUE)
    assert settings.VALUE == "On Testing CEX_binance"
    assert settings.cex_name == "binance"
    assert settings.cex_api == 'api_key'

def test_dynaconf_is_in_testing_env_DEX56(settings_dex_56):
    print(settings.VALUE)
    assert settings.VALUE == "On Testing DEX_56"
    assert settings.cex_name == ""
    assert settings.dex_chain_id == 56
    assert settings.dex_wallet_address == "0x1234567890123456789012345678901234567899"

def test_dynaconf_is_in_testing_env_DEX10(settings_dex_10):
    print(settings.VALUE)
    assert settings.VALUE == "On Testing DEX_10"
    assert settings.cex_name == ""
    assert settings.dex_chain_id == 10
    assert settings.dex_wallet_address == "0x1234567890123456789012345678901234567899"

@pytest.fixture(name="message")
def message_fixture():
    return "hello"

@pytest.fixture(name="command")
def command_message():
    return "/help"

@pytest.fixture(name="order")
def order_params():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'WBTC',
        'quantity': 1,
    }

@pytest.fixture(name="wrong_order")
def wrong_order():
    """Return order parameters."""
    return {
        'action': 'BUY',
        'instrument': 'NOTATHING',
        'quantity': 1,
    }


@pytest.mark.asyncio
async def test_listener_discord(settings_dex_56):
    print(settings.VALUE)
    listener = Listener()
    print(listener)
    assert listener is not None
    assert isinstance(listener, iamlistening.main.Listener)

@pytest.mark.asyncio
async def test_listener_telegram(message):
    listener = Listener()
    print(listener)
    assert listener is not None
    assert isinstance(listener, iamlistening.main.Listener)
    await listener.handle_message(message)
    msg = await listener.get_latest_message()
    print(msg)
    assert msg == "hello"

@pytest.mark.asyncio
async def test_listener_matrix(settings_dex_10,command):
    listener = Listener()
    print(listener)
    await listener.handle_message(command)
    msg = await listener.get_latest_message()
    print(msg)
    assert listener is not None
    assert isinstance(listener, iamlistening.main.Listener)
    assert msg == command

# @pytest.mark.asyncio
# async def test_parse_help():
#     """Test parse_message balance """
#     init_message= AsyncMock()
#     await parse_message('/help')
#     init_message.assert_called_once


# @pytest.mark.asyncio
# async def test_get_host_ip():
#     """Test get_host_ip """
#     output = get_host_ip()
#     assert output is not None


# @pytest.mark.asyncio
# async def test_init_message():
#     """Test the initialization message."""
#     await load_exchange()
#     output = await init_message()
#     assert output is not None
#     print(output)
#     # assert "🏓️" in output
#     # assert all(symbol in output for symbol in ["🕸️", "🏓", "💱", "🪪"])

# @pytest.mark.asyncio
# async def test_trading_switch():
#     """Test parse_message balance """
#     send_notification_mock = AsyncMock()
#     with patch('tt.utils.send_notification',send_notification_mock):
#         await load_exchange()
#         await parse_message('/trading')
#         assert settings.trading_enabled == False

def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200

def test_read_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200

def test_webhook_with_valid_auth():
    client = TestClient(app)
    payload = {"key": "123abc", "data": "buy BTC"}
    response = client.post("/webhook", json=payload)
    print(response)
    assert response is not None
    assert response.content.decode('utf-8') == '{"status":"OK"}'

def test_webhook_with_invalid_auth():
    client = TestClient(app)
    payload = {"key": "abc123", "data": "my_data"}
    print(payload)
    response = client.post("/webhook", json=payload)
    assert response.content.decode('utf-8') == '{"status":"ERROR"}'
