import json
import urllib.request
import urllib.parse
import yfinance as yf
from typing import Dict, Any

def search_ticker_symbol(company_name: str) -> str:
    """Search for a company's ticker symbol on Yahoo Finance."""
    query = urllib.parse.quote(company_name)
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=5"
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            quotes = data.get('quotes', [])
            
            if not quotes:
                return f"No ticker found for '{company_name}'."
                
            results = []
            for q in quotes:
                if 'symbol' in q and 'shortname' in q:
                    results.append(f"{q['symbol']} ({q['shortname']} - {q.get('exchange', 'Unknown')})")
            
            return "Found the following symbols:\n" + "\n".join(results)
    except Exception as e:
        return f"Error searching for ticker: {str(e)}"

def get_live_price(ticker: str) -> Dict[str, Any]:
    """Get live price and current day's volume for a given ticker."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "name": info.get("longName", info.get("shortName")),
        "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
        "currency": info.get("currency"),
        "day_high": info.get("dayHigh"),
        "day_low": info.get("dayLow"),
        "volume": info.get("volume"),
        "previous_close": info.get("previousClose")
    }

def get_company_fundamentals(ticker: str) -> Dict[str, Any]:
    """Get key financial metrics and fundamentals for a company."""
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "ticker": ticker,
        "market_cap": info.get("marketCap"),
        "currency": info.get("financialCurrency", info.get("currency")),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "dividend_yield": info.get("dividendYield"),
        "eps_trailing": info.get("trailingEps"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow")
    }

def get_historical_performance(ticker: str, period: str = "1mo") -> str:
    """
    Get historical price data.
    Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    """
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    if hist.empty:
        return f"No historical data found for {ticker} over period {period}."
    # Return as CSV string so it's compact for the LLM
    return hist.to_csv()
