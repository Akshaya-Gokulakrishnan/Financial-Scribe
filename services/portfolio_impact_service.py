import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PortfolioImpactService:
    """Service for calculating portfolio impact based on news sentiment and stock performance"""
    
    def __init__(self):
        pass
    
    def calculate_news_impact(self, portfolio, news_articles):
        """Calculate the impact of news sentiment on portfolio value"""
        try:
            impacts = {}
            total_portfolio_value = portfolio.get_total_value()
            
            if total_portfolio_value == 0:
                return impacts
            
            # Group news by stock symbol
            news_by_symbol = {}
            for article in news_articles:
                symbol = article.get('symbol', '')
                if symbol not in news_by_symbol:
                    news_by_symbol[symbol] = []
                news_by_symbol[symbol].append(article)
            
            # Calculate impact for each stock
            for stock in portfolio.stocks:
                symbol = stock.symbol
                stock_value = stock.get_current_value()
                weight_in_portfolio = (stock_value / total_portfolio_value) * 100
                
                # Get news sentiment for this stock
                stock_news = news_by_symbol.get(symbol, [])
                sentiment_impact = self._calculate_sentiment_impact(stock_news)
                
                # Calculate potential impact on portfolio
                portfolio_impact = (weight_in_portfolio * sentiment_impact) / 100
                
                # Calculate estimated price impact
                estimated_price_impact = stock.current_price * (sentiment_impact / 100)
                estimated_value_impact = stock.quantity * estimated_price_impact
                
                impacts[symbol] = {
                    'stock_symbol': symbol,
                    'stock_name': stock.company_name or symbol,
                    'current_value': stock_value,
                    'portfolio_weight': weight_in_portfolio,
                    'sentiment_score': sentiment_impact,
                    'portfolio_impact': portfolio_impact,
                    'estimated_price_impact': estimated_price_impact,
                    'estimated_value_impact': estimated_value_impact,
                    'news_count': len(stock_news),
                    'risk_level': self._get_risk_level(sentiment_impact, len(stock_news))
                }
            
            return impacts
            
        except Exception as e:
            logger.error(f"Error calculating news impact: {e}")
            return {}
    
    def _calculate_sentiment_impact(self, news_articles):
        """Calculate sentiment impact score from news articles"""
        if not news_articles:
            return 0.0
        
        # Weight more recent articles higher
        total_weighted_sentiment = 0.0
        total_weight = 0.0
        
        now = datetime.now()
        
        for article in news_articles:
            sentiment = article.get('sentiment', 0.0)
            published_date = article.get('published_date', now)
            
            # Calculate time-based weight (more recent = higher weight)
            if isinstance(published_date, datetime):
                time_diff = now - published_date
                hours_old = time_diff.total_seconds() / 3600
                
                # Weight decreases as news gets older
                if hours_old <= 1:
                    weight = 1.0  # Full weight for news less than 1 hour old
                elif hours_old <= 6:
                    weight = 0.8  # 80% weight for news less than 6 hours old
                elif hours_old <= 24:
                    weight = 0.6  # 60% weight for news less than 24 hours old
                else:
                    weight = 0.3  # 30% weight for older news
            else:
                weight = 0.5  # Default weight if date parsing fails
            
            total_weighted_sentiment += sentiment * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Calculate average weighted sentiment
        avg_sentiment = total_weighted_sentiment / total_weight
        
        # Convert to impact percentage (multiply by 10 for more visible impact)
        impact_percentage = avg_sentiment * 10
        
        # Cap the impact at reasonable levels
        return max(-20.0, min(20.0, impact_percentage))
    
    def _get_risk_level(self, sentiment_impact, news_count):
        """Determine risk level based on sentiment and news volume"""
        abs_impact = abs(sentiment_impact)
        
        if news_count >= 5 and abs_impact >= 10:
            return 'High'
        elif news_count >= 3 and abs_impact >= 5:
            return 'Medium'
        elif abs_impact >= 2:
            return 'Low'
        else:
            return 'Minimal'
    
    def get_portfolio_summary(self, portfolio, impacts):
        """Get overall portfolio impact summary"""
        try:
            if not impacts:
                return {
                    'total_sentiment_impact': 0.0,
                    'estimated_total_value_impact': 0.0,
                    'positive_impact_stocks': 0,
                    'negative_impact_stocks': 0,
                    'neutral_impact_stocks': 0,
                    'high_risk_stocks': 0,
                    'overall_risk_level': 'Minimal'
                }
            
            total_sentiment_impact = 0.0
            estimated_total_value_impact = 0.0
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            high_risk_count = 0
            
            for symbol, impact in impacts.items():
                sentiment = impact['sentiment_score']
                estimated_value_impact = impact['estimated_value_impact']
                risk_level = impact['risk_level']
                
                total_sentiment_impact += impact['portfolio_impact']
                estimated_total_value_impact += estimated_value_impact
                
                if sentiment > 1:
                    positive_count += 1
                elif sentiment < -1:
                    negative_count += 1
                else:
                    neutral_count += 1
                
                if risk_level == 'High':
                    high_risk_count += 1
            
            # Determine overall risk level
            total_stocks = len(impacts)
            if high_risk_count >= total_stocks * 0.5:
                overall_risk = 'High'
            elif high_risk_count >= total_stocks * 0.3:
                overall_risk = 'Medium'
            elif abs(total_sentiment_impact) >= 5:
                overall_risk = 'Medium'
            else:
                overall_risk = 'Low'
            
            return {
                'total_sentiment_impact': total_sentiment_impact,
                'estimated_total_value_impact': estimated_total_value_impact,
                'positive_impact_stocks': positive_count,
                'negative_impact_stocks': negative_count,
                'neutral_impact_stocks': neutral_count,
                'high_risk_stocks': high_risk_count,
                'overall_risk_level': overall_risk
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {
                'total_sentiment_impact': 0.0,
                'estimated_total_value_impact': 0.0,
                'positive_impact_stocks': 0,
                'negative_impact_stocks': 0,
                'neutral_impact_stocks': 0,
                'high_risk_stocks': 0,
                'overall_risk_level': 'Minimal'
            }
    
    def get_top_impact_stocks(self, impacts, limit=5):
        """Get stocks with highest impact (positive or negative)"""
        try:
            if not impacts:
                return []
            
            # Sort by absolute portfolio impact
            sorted_impacts = sorted(
                impacts.items(),
                key=lambda x: abs(x[1]['portfolio_impact']),
                reverse=True
            )
            
            return [impact[1] for impact in sorted_impacts[:limit]]
            
        except Exception as e:
            logger.error(f"Error getting top impact stocks: {e}")
            return []