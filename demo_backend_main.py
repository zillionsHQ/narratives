"""
Main FastAPI application exposing endpoints for cryptocurrency price data,
on‑chain metrics and developer activity.  This is a minimal demonstration
to show how public API endpoints can be orchestrated behind a simple
backend service.

Endpoints:
    GET /metrics/price/{symbol}
        Returns 24h ticker statistics for a given symbol from Binance.
    GET /metrics/daily_new_addresses
        Returns the daily new address count from Etherscan. Accepts optional
        query parameters `chainid`, `startdate`, `enddate` and `sort`.
    GET /metrics/github_activity/{owner}/{repo}
        Returns weekly commit activity for a repository from GitHub.
"""

from fastapi import FastAPI, HTTPException

from .connectors import binance, etherscan, github


app = FastAPI(title="Crypto Analytics Demo")


@app.get("/metrics/price/{symbol}")
async def get_price(symbol: str):
    """Fetch 24h ticker statistics for the given symbol from Binance.

    Args:
        symbol: The trading pair symbol, e.g. `BTCUSDT`.

    Returns:
        The JSON response from Binance's 24h ticker endpoint.
    """
    try:
        data = await binance.fetch_price(symbol)
        return data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/metrics/daily_new_addresses")
async def daily_new_addresses(
    chainid: str = "1",
    startdate: str | None = None,
    enddate: str | None = None,
    sort: str = "desc",
):
    """Fetch daily new address counts from Etherscan.

    Args:
        chainid: The chain identifier (default `1` for Ethereum mainnet).
        startdate: Start date in `yyyy-MM-dd` format.
        enddate: End date in `yyyy-MM-dd` format.
        sort: Sort order, either `asc` or `desc`.

    Returns:
        JSON result containing date and newAddressCount entries.
    """
    try:
        data = await etherscan.fetch_daily_new_addresses(
            chainid=chainid, startdate=startdate, enddate=enddate, sort=sort
        )
        return data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/metrics/github_activity/{owner}/{repo}")
async def github_activity(owner: str, repo: str):
    """Fetch weekly commit activity for a GitHub repository.

    Args:
        owner: GitHub owner or organization name.
        repo: Repository name.

    Returns:
        A list of weekly commit activity dictionaries or a message if the data
        is not yet available.
    """
    try:
        data = await github.fetch_weekly_commit_activity(owner, repo)
        return data
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc