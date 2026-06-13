from unittest.mock import AsyncMock

import pytest

from shared.realtime_data import RealtimeDataManager


@pytest.fixture
def manager():
    return RealtimeDataManager(api_key="test_key", api_secret="test_secret")


@pytest.mark.asyncio
async def test_get_price_returns_none_initially(manager):
    assert manager.get_price("BTC/USDT") is None


@pytest.mark.asyncio
async def test_get_all_prices_returns_empty_dict(manager):
    assert manager.get_all_prices() == {}


@pytest.mark.asyncio
async def test_get_candles_returns_empty_list(manager):
    assert manager.get_candles("BTC/USDT", "15m") == []


@pytest.mark.asyncio
async def test_on_price_callback_added(manager):
    cb = AsyncMock()
    manager.on_price(cb)
    assert len(manager._price_callbacks) == 1


@pytest.mark.asyncio
async def test_on_candle_callback_added(manager):
    cb = AsyncMock()
    manager.on_candle(cb)
    assert len(manager._candle_callbacks) == 1


@pytest.mark.asyncio
async def test_price_callback_invoked():
    cb = AsyncMock()
    mgr = RealtimeDataManager()
    mgr.on_price(cb)
    for c in mgr._price_callbacks:
        await c("BTC/USDT", 50000.0)
    cb.assert_awaited_once_with("BTC/USDT", 50000.0)


@pytest.mark.asyncio
async def test_candle_callback_invoked():
    cb = AsyncMock()
    mgr = RealtimeDataManager()
    mgr.on_candle(cb)
    for c in mgr._candle_callbacks:
        await c("ETH/USDT", "15m", [1, 2, 3, 4, 5])
    cb.assert_awaited_once_with("ETH/USDT", "15m", [1, 2, 3, 4, 5])


@pytest.mark.asyncio
async def test_stop_closes_exchange():
    mgr = RealtimeDataManager(api_key="x", api_secret="x")
    mock_ex = AsyncMock()
    mock_ex.close = AsyncMock()
    mock_ex.load_markets = AsyncMock()
    mgr._exchange = mock_ex

    await mgr.stop()
    mock_ex.close.assert_awaited_once()
    assert mgr._running is False


@pytest.mark.asyncio
async def test_get_price_after_direct_set(manager):
    manager._tickers["ETH/USDT"] = 2500.50
    assert manager.get_price("ETH/USDT") == 2500.50


@pytest.mark.asyncio
async def test_get_all_prices_after_set(manager):
    manager._tickers["BTC/USDT"] = 50000.0
    manager._tickers["ETH/USDT"] = 2500.0
    prices = manager.get_all_prices()
    assert prices == {"BTC/USDT": 50000.0, "ETH/USDT": 2500.0}


@pytest.mark.asyncio
async def test_get_candles_after_set(manager):
    manager._candles["BTC/USDT"] = {"15m": [[1, 2, 3, 4, 5]]}
    assert manager.get_candles("BTC/USDT", "15m") == [[1, 2, 3, 4, 5]]
