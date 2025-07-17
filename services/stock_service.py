import yfinance as yf
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class StockService:
    """Service for fetching stock data from Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def get_stock_data(self, symbol):
        """Get comprehensive stock data for a symbol"""
        try:
            # Check cache first
            if symbol in self.cache:
                cached_data, timestamp = self.cache[symbol]
                if (datetime.now() - timestamp).seconds < self.cache_timeout:
                    return cached_data
            
            # Fetch from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="2d")
            
            if hist.empty or not info:
                logger.warning(f"No data found for symbol: {symbol}")
                return None
            
            # Get current and previous close prices
            current_price = hist['Close'].iloc[-1] if len(hist) > 0 else 0
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            stock_data = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'current_price': float(current_price),
                'previous_close': float(previous_close),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('forwardPE'),
                'dividend_yield': info.get('dividendYield'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                'day_high': info.get('dayHigh'),
                'day_low': info.get('dayLow'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'beta': info.get('beta'),
                'eps': info.get('trailingEps'),
                'book_value': info.get('bookValue'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'return_on_equity': info.get('returnOnEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the data
            self.cache[symbol] = (stock_data, datetime.now())
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols):
        """Get data for multiple stocks"""
        results = {}
        for symbol in symbols:
            try:
                data = self.get_stock_data(symbol)
                if data:
                    results[symbol] = data
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                results[symbol] = None
        return results
    
    def get_stock_history(self, symbol, period="1mo"):
        """Get historical stock data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Convert to list of dictionaries
            history = []
            for date, row in hist.iterrows():
                history.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {e}")
            return None
    
    def validate_symbol(self, symbol):
        """Validate if a stock symbol exists"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except Exception:
            return False
    
    def search_stocks(self, query):
        """Search for stocks by name or symbol"""
        # Note: yfinance doesn't have a built-in search function
        # This is a basic implementation that validates symbols
        try:
            # Try to validate the query as a symbol
            if self.validate_symbol(query.upper()):
                data = self.get_stock_data(query.upper())
                if data:
                    return [{
                        'symbol': data['symbol'],
                        'name': data['company_name'],
                        'current_price': data['current_price']
                    }]
            return []
        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return []
