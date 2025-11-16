# mcp-crypto-server
MCP Crypto Server

A Python-based MCP (Model Context Protocol) server that provides real-time and historical cryptocurrency market data from multiple major exchanges using FastAPI, CCXT, CoinMarketCap, and CoinGecko.

Features
Real-Time Crypto Prices

Fetch the latest price for any crypto symbol (BTC, ETH, SOL, etc.).

Historical Data

Get historical OHLCV (Open, High, Low, Close, Volume) for any cryptocurrency.

Multi-Exchange Support

Switch between multiple exchanges easily:

Binance (via CCXT)

Coinbase (via CCXT)

Kraken (via CCXT)

Bybit (via CCXT)

OKX (optional)

CoinGecko (default)

CoinMarketCap (optional)

Using endpoint:

/exchange/set/{exchange_id}

Caching Layer

A 10-second in-memory cache reduces API calls and speeds up responses.

Robust Error Handling

Handled scenarios:

Invalid symbols

Unsupported exchanges

API failures

Missing price data

Clean Exchange Abstraction

Common interface for both CCXT and REST APIs.

Full Pytest Coverage

Includes tests for:

Cache

CCXT client

API endpoints

Exchange wrapper

Historical + real-time fetching

mcp-crypto-server/
│
├── server/
│   ├── cache.py
│   ├── ccxt_client.py
│   ├── cmc_client.py
│   ├── exchange.py
│   ├── data_fetcher.py
│   ├── main.py
│   ├── mcp_manifest.json
│   └── mcp_tool.py
│
├── tests/
│   ├── test_api.py
│   ├── test_cache.py
│   ├── test_ccxt_client.py
│   └── test_exchange.py
│
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md

Installation
Clone the repository
git clone https://github.com/naithik23/mcp-crypto-server.git
cd mcp-crypto-server

Create a virtual environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

Install dependencies
pip install -r requirements.txt

Run the Server
python -m server.main


Server runs at:

http://127.0.0.1:8000


API docs at:

http://127.0.0.1:8000/docs

API Endpoints
Root
GET /

Set Exchange
GET /exchange/set/{exchange_id}


Examples:

/exchange/set/binance

/exchange/set/coingecko

/exchange/set/cmc

Price Endpoint
GET /price/{symbol}


Example:

/price/BTC

Historical Endpoint
GET /historical/{symbol}?days=30

Run Tests
pytest -q


All tests will pass:

Cache tests

CCXT tests

API mock tests

Exchange abstraction tests

Assumptions

CoinGecko is used by default for public data.

CoinMarketCap and OKX require API keys.

CCXT handles supported exchanges internally.

Cache TTL = 10 seconds for performance.

Historical data format follows OHLCV standard.

Why this approach?

FastAPI → very fast + clean documentation

CCXT → supports 100+ exchanges

Clear separation of concerns (cache, clients, server)

Reliability through full test suite

Ready to plug into AI systems via MCP

Contact

If you have any questions, feel free to reach out:

Naithik
Email: gnannaithik2301@gmail.com

Thank you for reviewing!
