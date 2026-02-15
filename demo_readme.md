# Crypto Analytics Demo

This project demonstrates a minimal proof‑of‑concept backend for fetching cryptocurrency market, on‑chain and developer metrics using public APIs. It is not intended to be a production ready implementation but rather a starting point for a larger analytics platform.

## Features

* **Price data** – retrieves 24‑hour ticker statistics (price change, volume, etc.) for a given symbol from the Binance Futures market. The endpoint uses Binance's official REST API at `https://fapi.binance.com/fapi/v1/ticker/24hr`, which returns JSON formatted statistics over a rolling 24‑hour window【277163471933782†L96-L143】.
* **On‑chain data** – fetches the daily count of newly created addresses on Ethereum using the Etherscan API. The endpoint calls the `dailynewaddress` action on the `stats` module as documented by Etherscan【818986335177514†L80-L129】. An optional API key can be provided via the `ETHERSCAN_API_KEY` environment variable.
* **Developer activity** – queries the public GitHub API for weekly commit activity on a repository. The endpoint wraps the `stats/commit_activity` REST endpoint, which returns an array of weekly additions and deletions for repositories with fewer than 10,000 commits【911524837470379†L318-L329】.

## Prerequisites

* Python 3.10+ installed on your system.
* `pip` for installing dependencies.
* An optional Etherscan API key (set the `ETHERSCAN_API_KEY` environment variable) to increase rate limits for on‑chain queries.
* Internet access to call the public API endpoints.

## Installation

Create a virtual environment (optional but recommended) and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the API server

From the project root, run the FastAPI application with Uvicorn:

```bash
uvicorn backend.main:app --reload
```

This will start the API server on `http://localhost:8000` with hot reloading enabled.

## Using the demo frontend

Open the `frontend/index.html` file in a web browser while the API server is running. The page will make requests to the local API and display JSON output for:

* Price metrics for the `BTCUSDT` symbol
* Daily new addresses on Ethereum (last week)
* Weekly commit activity for the `zillionsHQ/narratives` repository

## Caveats

* This project skips database persistence, background job queues and comprehensive error handling for simplicity.
* The API keys for Etherscan and GitHub are optional; however, using keys will improve reliability and avoid stricter rate limits.
* The endpoints may return messages indicating the data is still being generated (e.g. GitHub returns HTTP 202 for stats on very large repositories). See the respective API documentation for details【911524837470379†L318-L327】.
