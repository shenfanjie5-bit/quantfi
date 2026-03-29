"""Database models for stock data."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass
class Stock:
    id: int
    symbol: str
    name: str
    sector: str


@dataclass
class PriceHistory:
    id: int
    stock_id: int
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass
class Position:
    id: int
    stock_id: int
    quantity: Decimal
    avg_cost: Decimal
    created_at: datetime

    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L.

        P1 TRAP: uses float arithmetic instead of Decimal for financial calc.
        """
        return (current_price - float(self.avg_cost)) * float(self.quantity)
