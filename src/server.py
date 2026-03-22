from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import List

from global_stocks import search_ticker_symbol, get_live_price, get_company_fundamentals, get_historical_performance
from bhavdata_analyzer import query_bhavdata
from dashboard_generator import generate_stock_dashboard

# Initialize FastMCP Server
mcp = FastMCP("StockAnalyzer")

@mcp.tool()
def find_ticker(company_name: str = Field(description="The name of the company to find the Yahoo Finance ticker for, e.g., 'TCS' -> 'TCS.NS'")):
    """Find the exact ticker symbol for a given company name"""
    return search_ticker_symbol(company_name)

@mcp.tool()
def get_stock_price(ticker: str = Field(description="The Yahoo Finance ticker symbol, e.g., 'RELIANCE.NS', 'AAPL'")):
    """Get the current live price, day high/low, and trading volume for a stock"""
    try:
        return str(get_live_price(ticker))
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"

@mcp.tool()
def get_stock_fundamentals(ticker: str = Field(description="The Yahoo Finance ticker symbol")):
    """Get fundamental financial metrics like Market Cap, P/E ratio, and dividend yield"""
    try:
        return str(get_company_fundamentals(ticker))
    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {str(e)}"

@mcp.tool()
def get_stock_history(ticker: str = Field(description="The Yahoo Finance ticker symbol"), period: str = Field(description="Time period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '5y', 'max'", default="1mo")):
    """Get raw historical daily price data as CSV"""
    try:
        return get_historical_performance(ticker, period)
    except Exception as e:
        return f"Error fetching history for {ticker}: {str(e)}"

@mcp.tool()
def build_interactive_dashboard(ticker: str = Field(description="The Yahoo Finance ticker symbol"), period: str = Field(description="Time period: '1mo', '3mo', '6mo', '1y'", default="1mo")):
    """Generate a fully interactive, locally hosted HTML dashboard showing the stock's performance graph. Use this when the user explicitly asks to SEE a graph or visualization."""
    return generate_stock_dashboard(ticker, period)

@mcp.tool()
def analyze_bhavdata(file_paths: List[str] = Field(description="List of absolute paths to the local BhavData CSV files"), sql_query: str = Field(description="SQL query to run against the loaded BhavData. The table is always named 'bhavdata'. Example: SELECT SYMBOL, CLOSE FROM bhavdata LIMIT 10")):
    """Query local NSE BhavData CSV files dynamically via SQL to analyze trading activity."""
    return query_bhavdata(file_paths, sql_query)

if __name__ == "__main__":
    mcp.run(transport='stdio')
