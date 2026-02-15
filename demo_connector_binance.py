"""Binance connector for fetching public market data.

This module implements a minimal asynchronous function to retrieve
24‑hour ticker statistics for a given symbol using the Binance futures
REST API. For more detailed market data or spot endpoints, consult the
official documentation at https://developers.binance.com/【277163471933782†L96-L143】.
"""

import httpx


BASE_URL = "https://fapi.binance.com/fapi/v1"


async def fetch_price(symbol: str) -> dict:
    """Return 24h price statistics for a trading pair from Binance.

    The endpoint returns fields such as priceChange, priceChangePercent,
    weightedAvgPrice, lastPrice, volume and more within a 24‑hour rolling
    window【277163471933782†L96-L143】.

    Args:
        symbol: Trading pair symbol (e.g. 'BTCUSDT', 'ETHUSDT').

    Raises:
        httpx.HTTPStatusError: If the API call fails.

    Returns:
        A dictionary containing the JSON response from Binance.
    """
    url = f"{BASE_URL}/ticker/24hr"
    params = {"symbol": symbol.upper()}
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()