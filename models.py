from app import db
from datetime import datetime
from sqlalchemy import func

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="My Portfolio")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to stocks
    stocks = db.relationship('Stock', backref='portfolio', lazy=True, cascade="all, delete-orphan")
    
    def get_total_value(self):
        """Calculate total portfolio value"""
        return sum(stock.get_current_value() for stock in self.stocks)
    
    def get_total_cost(self):
        """Calculate total cost basis"""
        return sum(stock.get_cost_basis() for stock in self.stocks)
    
    def get_total_gain_loss(self):
        """Calculate total gain/loss"""
        return self.get_total_value() - self.get_total_cost()
    
    def get_daily_gain_loss(self):
        """Calculate daily gain/loss"""
        return sum(stock.get_daily_gain_loss() for stock in self.stocks)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    company_name = db.Column(db.String(200))
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, default=0.0)
    previous_close = db.Column(db.Float, default=0.0)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Market data
    market_cap = db.Column(db.Float)
    pe_ratio = db.Column(db.Float)
    dividend_yield = db.Column(db.Float)
    
    # Sentiment data
    news_sentiment = db.Column(db.Float, default=0.0)  # -1 to 1 scale
    sentiment_updated = db.Column(db.DateTime)
    
    def get_current_value(self):
        """Get current market value of holdings"""
        return self.quantity * self.current_price
    
    def get_cost_basis(self):
        """Get cost basis of holdings"""
        return self.quantity * self.purchase_price
    
    def get_gain_loss(self):
        """Get total gain/loss"""
        return self.get_current_value() - self.get_cost_basis()
    
    def get_gain_loss_percentage(self):
        """Get gain/loss percentage"""
        cost_basis = self.get_cost_basis()
        if cost_basis == 0:
            return 0
        return (self.get_gain_loss() / cost_basis) * 100
    
    def get_daily_gain_loss(self):
        """Get daily gain/loss"""
        if self.previous_close == 0:
            return 0
        return self.quantity * (self.current_price - self.previous_close)
    
    def get_daily_gain_loss_percentage(self):
        """Get daily gain/loss percentage"""
        if self.previous_close == 0:
            return 0
        return ((self.current_price - self.previous_close) / self.previous_close) * 100
    
    def get_portfolio_impact(self):
        """Calculate this stock's impact on the portfolio"""
        total_portfolio_value = self.portfolio.get_total_value()
        if total_portfolio_value == 0:
            return 0
        return (self.get_current_value() / total_portfolio_value) * 100

class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    url = db.Column(db.String(1000))
    published_date = db.Column(db.DateTime)
    sentiment_score = db.Column(db.Float, default=0.0)
    sentiment_label = db.Column(db.String(20))  # positive, negative, neutral
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NewsArticle {self.title[:50]}...>'
