import pytest

from core.services.PositionMonitor import PositionMonitor
from tests.mocks.mock_price_provider import MockPriceProvider

mock_price_provider = MockPriceProvider()
position_monitor = PositionMonitor(mock_price_provider)

@pytest.mark.asyncio
async def test_check_position_pnl_must_return_signal_true() -> None:
    stock = "TEST"
    your_buy_price = 99
    stock_count = 1
    growth_threshold = 0.1
    loss_threshold = 0.2

    result = await position_monitor.check_position_pnl(stock=stock, your_buy_price=your_buy_price,
                                                     stock_count=stock_count,
                                                 growth_threshold=growth_threshold, loss_threshold=loss_threshold)
    assert result['signal'] is True


@pytest.mark.asyncio
async def test_check_position_pnl_must_return_signal_true_and_stop_loss() -> None:
    stock = "TEST"
    your_buy_price = 101
    stock_count = 1
    growth_threshold = 0.1
    loss_threshold = 0.2

    result = await position_monitor.check_position_pnl(stock=stock, your_buy_price=your_buy_price, stock_count=stock_count,
                                                 growth_threshold=growth_threshold, loss_threshold=loss_threshold)
    assert result['signal'] is True and result['type'] == 'STOP_LOSS'

@pytest.mark.asyncio
async def test_check_position_pnl_must_return_signal_true_and_take_profit()-> None:
    stock = "TEST"
    your_buy_price = 98
    stock_count = 1
    growth_threshold = 0.1
    loss_threshold = 0.2

    result = await position_monitor.check_position_pnl(stock=stock, your_buy_price=your_buy_price, stock_count=stock_count,
                                                 growth_threshold=growth_threshold, loss_threshold=loss_threshold)

    assert result['signal'] is True and result['type'] == 'TAKE_PROFIT'

@pytest.mark.asyncio
async def test_check_position_pnl_must_return_signal_false() -> None:
    stock = "TEST"
    your_buy_price = 100
    stock_count = 1
    growth_threshold = 0.1
    loss_threshold = 0.2

    result = await position_monitor.check_position_pnl(stock=stock, your_buy_price=your_buy_price, stock_count=stock_count,
                                                 growth_threshold=growth_threshold, loss_threshold=loss_threshold)
    assert result['signal'] is False

