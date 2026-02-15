"""Etherscan connector for on‑chain metrics.

This module defines an asynchronous function to fetch the daily number of
new addresses on Ethereum (or another supported chain) via the Etherscan
API. The `dailynewaddress` endpoint is part of the stats module and
requires an API key for consistent access. See the official docs for
details【818986335177514†L80-L129】.
"""

import os
from typing import Optional

import httpx


ETHERSCAN_BASE_URL = "https://api.etherscan.io/v2/api"


async def fetch_daily_new_addresses(
    chainid: str = "1",
    startdate: Optional[str] = None,
    enddate: Optional[str] = None,
    sort: str = "desc",
) -> dict:
    """Retrieve daily new address counts from the Etherscan API.

    Args:
        chainid: Chain identifier (default "1" for Ethereum mainnet).
        startdate: Optional start date in `yyyy-MM-dd` format.
        enddate: Optional end date in `yyyy-MM-dd` format.
        sort: Sort order, `asc` or `desc`. Defaults to `desc`.

    Returns:
        Parsed JSON response from Etherscan containing newAddressCount per day.
    """
    api_key = os.getenv("ETHERSCAN_API_KEY", "YourApiKeyToken")
    params: dict[str, str] = {
        "chainid": chainid,
        "module": "stats",
        "action": "dailynewaddress",
        "apikey": api_key,
        "sort": sort,
    }
    if startdate:
        params["startdate"] = startdate
    if enddate:
        params["enddate"] = enddate
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(ETHERSCAN_BASE_URL, params=params)
        response.raise_for_status()
        return response.json()