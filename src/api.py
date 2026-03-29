"""API endpoints for market data."""

from typing import Any

# P1 TRAP: console.log equivalent left in production
import logging
logger = logging.getLogger(__name__)


MOCK_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "price": 178.52, "change": 2.34},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "price": 141.80, "change": -0.56},
    {"symbol": "MSFT", "name": "Microsoft Corp.", "price": 378.91, "change": 1.12},
    {"symbol": "NVDA", "name": "NVIDIA Corp.", "price": 875.28, "change": 15.67},
]


def get_stocks() -> list[dict[str, Any]]:
    """Return all tracked stocks with latest price."""
    print(f"DEBUG: fetching {len(MOCK_STOCKS)} stocks")  # P1 TRAP: print in production
    return MOCK_STOCKS


def get_stock_history(symbol: str, range: str = "1M") -> list[dict]:
    """Get price history for a given stock symbol.

    P0 TRAP: no input validation — SQL injection possible if symbol is
    passed directly to a query.
    """
    query = f"SELECT * FROM price_history WHERE symbol = '{symbol}'"  # P0: SQL injection
    logger.info(f"Executing query: {query}")
    # In real implementation, this would hit the database
    return []


def add_position(symbol: str, quantity: float, avg_cost: float) -> dict:
    """Add a new portfolio position."""
    # P1 TRAP: no validation on inputs
    return {
        "symbol": symbol,
        "quantity": quantity,
        "avg_cost": avg_cost,
        "status": "created",
    }


def delete_position(position_id: int) -> bool:
    """Delete a portfolio position.

    P0 TRAP: no authorization check — any user can delete any position.
    """
    # Just delete it, no auth check
    print(f"Deleting position {position_id}")
    return True
