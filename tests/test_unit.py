"""
 TT test
"""
from unittest.mock import AsyncMock, MagicMock, patch, call
import pytest
import ccxt
import dxsp
import iamlistening
from iamlistening import Listener
from fastapi.testclient import TestClient
from tt.bot import app
from tt.utils import (parse_message, send_notification,
    load_exchange, execute_order,
    init_message, get_name, get_quote, get_trading_asset_balance,
    get_account, get_account_balance,
    get_account_position,
    get_account_margin,
    get_host_ip, get_ping)
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
        'instrument': 'UNI',
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

@pytest.mark.asyncio
async def test_parse_help():
    """Test parse_message balance """
    init_message= AsyncMock()
    await parse_message('/help')
    init_message.assert_called_once


@pytest.mark.asyncio
async def test_parse_bal():
    """Test parse_message balance """
    send_notification_mock = AsyncMock()
    get_account_balance= AsyncMock()
    await load_exchange()
    await parse_message('/bal')
    get_account_balance.assert_called_once

@pytest.mark.asyncio
async def test_parse_quote(caplog):
    """Test parse_message balance """
    get_quote= AsyncMock("WBTC")
    await load_exchange()
    result = await parse_message('/q WBTC')
    assert 'quote [1, 0]' in caplog.text


@pytest.mark.asyncio
async def test_send_notification(caplog):
    """Test send_notification function"""
    message = '<code>test message</code>'
    await send_notification(message)
    assert 'There are no service(s) to notify' in caplog.text


@pytest.mark.asyncio
async def test_get_host_ip():
    """Test get_host_ip """
    output = get_host_ip()
    assert output is not None


@pytest.mark.asyncio
async def test_get_ping():
    """Test get_host_ip """
    output = get_host_ip()
    assert output is not None

@pytest.mark.asyncio
async def test_dex_load_exchange():
    """test exchange dex"""
    exchange = await load_exchange()
    account = await get_account(exchange)
    print(exchange)
    assert exchange is not None
    assert account == "1 - 34567890"
    assert isinstance(exchange, dxsp.DexSwap)


@pytest.mark.asyncio
async def test_cex_load_exchange(settings_cex):
    """test exchange cex"""
    mock_ccxt = MagicMock()
    mock_ccxt.cex_client = MagicMock()
    mock_exchange = MagicMock()
    with patch.dict("sys.modules", ccxt=mock_ccxt):
        mock_ccxt.cex_client.return_value = mock_exchange
        exchange = await load_exchange()
        name = await get_name()
        assert exchange is not None
        assert name == 'binance'
        assert isinstance(exchange, ccxt.binance)


# @pytest.mark.asyncio
# async def test_execute_order(caplog, order):
#     await load_exchange()
#     execute_mock = AsyncMock()
#     with patch('tt.utils.execute_order',execute_mock):
#         trade_confirmation = await execute_order(order)
#         assert "⚠️ order execution:" not in caplog.text


@pytest.mark.asyncio
async def test_failed_execute_order(caplog, order):
    await load_exchange()
    trade_confirmation = await execute_order(order)
    assert "🗓️" not in caplog.text


@pytest.mark.asyncio
async def test_get_quote():
    """Test get_quote """
    await load_exchange()
    output = await get_quote("WBTC")
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_account_balance():
    """Test get_account_balance."""
    await load_exchange()
    output = await get_account_balance()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_trading_asset_balance():
    """Test get_asset_trading_balance."""
    await load_exchange()
    output = await get_trading_asset_balance()
    print(output)
    assert output is not None

    
@pytest.mark.asyncio
async def test_get_account_position():
    """Test get_account_positions."""
    await load_exchange() 
    output = await get_account_position()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_get_account_margin():
    """Test get_account_margin """
    await load_exchange() 
    output = await get_account_margin()
    print(output)
    assert output is not None


@pytest.mark.asyncio
async def test_init_message():
    """Test test_init_message."""
    await load_exchange()
    output = await init_message()
    print(output)
    assert output is not None

@pytest.mark.asyncio
async def test_trading_switch():
    """Test parse_message balance """
    send_notification_mock = AsyncMock()
    with patch('tt.utils.send_notification',send_notification_mock):
        await load_exchange()
        await parse_message('/trading')
        assert settings.trading_enabled == False

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
