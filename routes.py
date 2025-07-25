from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Portfolio, Stock, NewsArticle
from services.stock_service import StockService
from services.news_service import NewsService
from services.sentiment_service import SentimentService
from services.portfolio_impact_service import PortfolioImpactService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@app.route('/')
def dashboard():
    """Main dashboard showing portfolio overview"""
    try:
        # Get or create default portfolio
        portfolio = Portfolio.query.first()
        if not portfolio:
            portfolio = Portfolio(name="My Portfolio")
            db.session.add(portfolio)
            db.session.commit()
        
        # Update stock prices
        stock_service = StockService()
        for stock in portfolio.stocks:
            try:
                stock_data = stock_service.get_stock_data(stock.symbol)
                if stock_data:
                    stock.current_price = stock_data.get('current_price', stock.current_price)
                    stock.previous_close = stock_data.get('previous_close', stock.previous_close)
                    stock.company_name = stock_data.get('company_name', stock.company_name)
                    stock.market_cap = stock_data.get('market_cap')
                    stock.pe_ratio = stock_data.get('pe_ratio')
                    stock.dividend_yield = stock_data.get('dividend_yield')
            except Exception as e:
                logger.error(f"Error updating stock {stock.symbol}: {e}")
        
        db.session.commit()
        
        # Get recent news for portfolio stocks and update sentiment
        news_service = NewsService()
        sentiment_service = SentimentService()
        portfolio_impact_service = PortfolioImpactService()
        recent_news = []
        stock_news_map = {}  # NEW: Map symbol to news list
        
        for stock in portfolio.stocks:
            try:
                stock_news = news_service.get_stock_news(stock.symbol, limit=5)
                # Calculate sentiment for each news article
                sentiments = []
                for article in stock_news:
                    sentiment = sentiment_service.analyze_sentiment(article.get('title', ''))
                    article['sentiment'] = sentiment
                    article['sentiment_label'] = sentiment_service.get_sentiment_label(sentiment)
                    article['sentiment_color'] = sentiment_service.get_sentiment_color(sentiment)
                    sentiments.append(sentiment)
                # Update stock sentiment with average
                if sentiments:
                    avg_sentiment = sum(sentiments) / len(sentiments)
                    stock.news_sentiment = avg_sentiment
                    stock.sentiment_updated = datetime.utcnow()
                recent_news.extend(stock_news)
                stock_news_map[stock.symbol] = stock_news  # NEW: Add to map
            except Exception as e:
                logger.error(f"Error fetching news for {stock.symbol}: {e}")
        
        # Commit sentiment updates
        db.session.commit()
        
        # Calculate portfolio impact from news sentiment
        portfolio_impacts = portfolio_impact_service.calculate_news_impact(portfolio, recent_news)
        portfolio_summary = portfolio_impact_service.get_portfolio_summary(portfolio, portfolio_impacts)
        top_impact_stocks = portfolio_impact_service.get_top_impact_stocks(portfolio_impacts, limit=5)
        
        # Sort by date
        recent_news.sort(key=lambda x: x.get('published_date', datetime.now()), reverse=True)
        recent_news = recent_news[:15]  # Limit to 15 most recent
        
        return render_template('dashboard.html', 
                             portfolio=portfolio, 
                             recent_news=recent_news,
                             portfolio_impacts=portfolio_impacts,
                             portfolio_summary=portfolio_summary,
                             top_impact_stocks=top_impact_stocks,
                             stock_news_map=stock_news_map)  # NEW: Pass map
    
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        flash(f"Error loading dashboard: {str(e)}", 'error')
        return render_template('dashboard.html', portfolio=None, recent_news=[])

@app.route('/add_stock', methods=['GET', 'POST'])
def add_stock():
    """Add a new stock to the portfolio"""
    if request.method == 'POST':
        try:
            symbol = request.form.get('symbol', '').upper().strip()
            quantity = float(request.form.get('quantity', 0))
            purchase_price = float(request.form.get('purchase_price', 0))
            
            if not symbol or quantity <= 0 or purchase_price <= 0:
                flash('Please provide valid stock symbol, quantity, and purchase price.', 'error')
                return render_template('add_stock.html')
            
            # Get or create portfolio
            portfolio = Portfolio.query.first()
            if not portfolio:
                portfolio = Portfolio(name="My Portfolio")
                db.session.add(portfolio)
                db.session.commit()
            
            # Validate stock symbol and get current data
            stock_service = StockService()
            stock_data = stock_service.get_stock_data(symbol)
            
            if not stock_data:
                flash(f'Invalid stock symbol: {symbol}', 'error')
                return render_template('add_stock.html')
            
            # Check if stock already exists in portfolio
            existing_stock = Stock.query.filter_by(symbol=symbol, portfolio_id=portfolio.id).first()
            if existing_stock:
                # Update existing stock
                existing_stock.quantity += quantity
                existing_stock.purchase_price = ((existing_stock.purchase_price * (existing_stock.quantity - quantity)) + 
                                               (purchase_price * quantity)) / existing_stock.quantity
                flash(f'Updated existing position for {symbol}', 'success')
            else:
                # Create new stock
                stock = Stock(
                    symbol=symbol,
                    company_name=stock_data.get('company_name', symbol),
                    quantity=quantity,
                    purchase_price=purchase_price,
                    current_price=stock_data.get('current_price', purchase_price),
                    previous_close=stock_data.get('previous_close', purchase_price),
                    portfolio_id=portfolio.id,
                    market_cap=stock_data.get('market_cap'),
                    pe_ratio=stock_data.get('pe_ratio'),
                    dividend_yield=stock_data.get('dividend_yield')
                )
                db.session.add(stock)
                flash(f'Added {symbol} to portfolio', 'success')
            
            db.session.commit()
            
            # Get news and sentiment for new stock
            try:
                news_service = NewsService()
                sentiment_service = SentimentService()
                
                news_articles = news_service.get_stock_news(symbol, limit=5)
                if news_articles:
                    sentiments = []
                    for article in news_articles:
                        sentiment = sentiment_service.analyze_sentiment(article.get('title', ''))
                        sentiments.append(sentiment)
                        
                        # Save news article
                        news_article = NewsArticle(
                            stock_symbol=symbol,
                            title=article.get('title', ''),
                            url=article.get('url', ''),
                            sentiment_score=sentiment,
                            sentiment_label='positive' if sentiment > 0.1 else 'negative' if sentiment < -0.1 else 'neutral'
                        )
                        db.session.add(news_article)
                    
                    # Update stock sentiment
                    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
                    stock = Stock.query.filter_by(symbol=symbol, portfolio_id=portfolio.id).first()
                    if stock:
                        stock.news_sentiment = avg_sentiment
                    
                    db.session.commit()
            except Exception as e:
                logger.error(f"Error fetching news/sentiment for {symbol}: {e}")
            
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash('Please enter valid numeric values for quantity and price.', 'error')
            return render_template('add_stock.html')
        except Exception as e:
            logger.error(f"Error adding stock: {e}")
            flash(f'Error adding stock: {str(e)}', 'error')
            return render_template('add_stock.html')
    
    return render_template('add_stock.html')

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    """Show detailed information for a specific stock"""
    try:
        # Get the stock from the portfolio
        stock = Stock.query.filter_by(symbol=symbol.upper()).first()
        if not stock:
            flash('Stock not found in portfolio', 'error')
            return redirect(url_for('dashboard'))
        
        # Get recent news for this specific stock
        news_service = NewsService()
        sentiment_service = SentimentService()
        
        stock_news = news_service.get_stock_news(stock.symbol, limit=20)
        
        # Calculate sentiment for each news article
        for article in stock_news:
            sentiment = sentiment_service.analyze_sentiment(article.get('title', ''))
            article['sentiment'] = sentiment
            article['sentiment_label'] = sentiment_service.get_sentiment_label(sentiment)
            article['sentiment_color'] = sentiment_service.get_sentiment_color(sentiment)
        
        # Update stock with fresh market data
        stock_service = StockService()
        stock_data = stock_service.get_stock_data(stock.symbol)
        
        if stock_data:
            stock.current_price = stock_data.get('current_price', stock.current_price)
            stock.previous_close = stock_data.get('previous_close', stock.previous_close)
            stock.change_percent = stock_data.get('change_percent', stock.change_percent)
            stock.volume = stock_data.get('volume', stock.volume)
            stock.market_cap = stock_data.get('market_cap', stock.market_cap)
            stock.pe_ratio = stock_data.get('pe_ratio', stock.pe_ratio)
            stock.dividend_yield = stock_data.get('dividend_yield', stock.dividend_yield)
            stock.week_52_high = stock_data.get('week_52_high', stock.week_52_high)
            stock.week_52_low = stock_data.get('week_52_low', stock.week_52_low)
            stock.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        return render_template('stock_detail.html', stock=stock, news=stock_news)
        
    except Exception as e:
        logger.error(f"Error loading stock detail for {symbol}: {e}")
        flash('Error loading stock details. Please try again.', 'error')
        return redirect(url_for('dashboard'))

@app.route('/remove_stock/<int:stock_id>')
def remove_stock(stock_id):
    """Remove a stock from the portfolio"""
    try:
        stock = Stock.query.get_or_404(stock_id)
        symbol = stock.symbol
        db.session.delete(stock)
        db.session.commit()
        flash(f'Removed {symbol} from portfolio', 'success')
    except Exception as e:
        logger.error(f"Error removing stock: {e}")
        flash(f'Error removing stock: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/api/stock_data/<symbol>')
def get_stock_data(symbol):
    """API endpoint to get stock data"""
    try:
        stock_service = StockService()
        data = stock_service.get_stock_data(symbol.upper())
        if data:
            return jsonify(data)
        else:
            return jsonify({'error': 'Stock not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh_portfolio')
def refresh_portfolio():
    """API endpoint to refresh portfolio data"""
    try:
        portfolio = Portfolio.query.first()
        if not portfolio:
            return jsonify({'error': 'No portfolio found'}), 404
        
        stock_service = StockService()
        updated_stocks = []
        
        for stock in portfolio.stocks:
            try:
                stock_data = stock_service.get_stock_data(stock.symbol)
                if stock_data:
                    stock.current_price = stock_data.get('current_price', stock.current_price)
                    stock.previous_close = stock_data.get('previous_close', stock.previous_close)
                    updated_stocks.append(stock.symbol)
            except Exception as e:
                logger.error(f"Error updating {stock.symbol}: {e}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'updated_stocks': updated_stocks,
            'total_value': portfolio.get_total_value(),
            'daily_gain_loss': portfolio.get_daily_gain_loss()
        })
    except Exception as e:
        logger.error(f"Error refreshing portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
