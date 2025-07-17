from textblob import TextBlob
import logging
import re

logger = logging.getLogger(__name__)

class SentimentService:
    """Service for analyzing sentiment of text content"""
    
    def __init__(self):
        # Define financial keywords for context-aware sentiment
        self.positive_keywords = [
            'profit', 'gain', 'growth', 'increase', 'rise', 'up', 'bullish', 
            'buy', 'strong', 'beat', 'exceed', 'outperform', 'positive', 
            'boost', 'surge', 'rally', 'upgrade', 'dividend', 'earnings'
        ]
        
        self.negative_keywords = [
            'loss', 'drop', 'decline', 'fall', 'down', 'bearish', 'sell',
            'weak', 'miss', 'underperform', 'negative', 'plunge', 'crash',
            'downgrade', 'cut', 'recession', 'bankruptcy', 'lawsuit'
        ]
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of given text"""
        try:
            if not text or not isinstance(text, str):
                return 0.0
            
            # Clean the text
            cleaned_text = self.clean_text(text)
            
            # Get base sentiment using TextBlob
            blob = TextBlob(cleaned_text)
            base_sentiment = blob.sentiment.polarity
            
            # Apply financial context weighting
            financial_sentiment = self.get_financial_sentiment(cleaned_text)
            
            # Combine base sentiment with financial context
            final_sentiment = (base_sentiment * 0.7) + (financial_sentiment * 0.3)
            
            # Normalize to -1 to 1 range
            final_sentiment = max(-1.0, min(1.0, final_sentiment))
            
            return round(final_sentiment, 3)
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0
    
    def clean_text(self, text):
        """Clean and preprocess text for sentiment analysis"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.,!?;:]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.lower()
    
    def get_financial_sentiment(self, text):
        """Get sentiment score based on financial keywords"""
        words = text.lower().split()
        
        positive_count = 0
        negative_count = 0
        
        for word in words:
            if any(keyword in word for keyword in self.positive_keywords):
                positive_count += 1
            if any(keyword in word for keyword in self.negative_keywords):
                negative_count += 1
        
        total_keywords = positive_count + negative_count
        
        if total_keywords == 0:
            return 0.0
        
        # Calculate sentiment score
        sentiment_score = (positive_count - negative_count) / total_keywords
        
        return sentiment_score
    
    def analyze_multiple_texts(self, texts):
        """Analyze sentiment for multiple texts"""
        sentiments = []
        
        for text in texts:
            sentiment = self.analyze_sentiment(text)
            sentiments.append(sentiment)
        
        return sentiments
    
    def get_aggregate_sentiment(self, texts):
        """Get aggregate sentiment score for multiple texts"""
        if not texts:
            return 0.0
        
        sentiments = self.analyze_multiple_texts(texts)
        
        if not sentiments:
            return 0.0
        
        # Calculate weighted average (recent texts have more weight)
        weights = [1.0 / (i + 1) for i in range(len(sentiments))]
        weighted_sum = sum(s * w for s, w in zip(sentiments, weights))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
    
    def get_sentiment_label(self, sentiment_score):
        """Get human-readable sentiment label"""
        if sentiment_score > 0.1:
            return "Positive"
        elif sentiment_score < -0.1:
            return "Negative"
        else:
            return "Neutral"
    
    def get_sentiment_color(self, sentiment_score):
        """Get color code for sentiment visualization"""
        if sentiment_score > 0.1:
            return "success"  # Green
        elif sentiment_score < -0.1:
            return "danger"   # Red
        else:
            return "secondary"  # Gray
    
    def analyze_news_sentiment(self, news_articles):
        """Analyze sentiment for news articles"""
        results = []
        
        for article in news_articles:
            title = article.get('title', '')
            content = article.get('content', '')
            
            # Analyze title sentiment (more weight)
            title_sentiment = self.analyze_sentiment(title)
            
            # Analyze content sentiment if available
            content_sentiment = 0.0
            if content:
                content_sentiment = self.analyze_sentiment(content)
            
            # Combine sentiments (title has more weight)
            final_sentiment = (title_sentiment * 0.8) + (content_sentiment * 0.2)
            
            results.append({
                'title': title,
                'sentiment_score': final_sentiment,
                'sentiment_label': self.get_sentiment_label(final_sentiment),
                'sentiment_color': self.get_sentiment_color(final_sentiment),
                'url': article.get('url', ''),
                'source': article.get('source', ''),
                'published_date': article.get('published_date', ''),
                'symbol': article.get('symbol', '')
            })
        
        return results
