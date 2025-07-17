# Stock Portfolio Manager

## Overview

This is a Flask-based stock portfolio management application that allows users to track their stock investments, view real-time market data, and analyze sentiment from financial news. The application provides a comprehensive dashboard with portfolio analytics, individual stock performance tracking, and market sentiment analysis.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL support
- **Application Structure**: Modular design with separate services for different functionalities
- **Session Management**: Flask sessions with configurable secret key

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6
- **Charts**: Chart.js for data visualization
- **Styling**: Custom CSS with CSS variables for theming

### Database Schema
- **Portfolio**: Main portfolio entity with relationship to stocks
- **Stock**: Individual stock holdings with market data and sentiment information
- **NewsArticle**: Referenced but not fully implemented in the current codebase

## Key Components

### Models (models.py)
- **Portfolio Model**: Manages portfolio metadata and aggregated calculations
- **Stock Model**: Stores individual stock data including purchase info, current prices, and market metrics
- **Relationships**: One-to-many relationship between Portfolio and Stock with cascade deletion

### Services Layer
- **StockService**: Integrates with Yahoo Finance API (yfinance) for real-time stock data
- **NewsService**: Web scraping service for Google News to fetch stock-related articles
- **SentimentService**: Text analysis using TextBlob with financial keyword weighting

### Route Handlers (routes.py)
- **Dashboard Route**: Main application entry point with portfolio overview
- **Stock Management**: Add/edit/delete stock operations
- **Data Updates**: Real-time price updates and news fetching

### Frontend Components
- **Dashboard**: Portfolio overview with performance metrics and stock listings
- **Add Stock Form**: Interface for adding new stocks to portfolio
- **Base Template**: Common navigation and layout structure

## Data Flow

1. **User Access**: User visits dashboard route
2. **Portfolio Initialization**: System creates default portfolio if none exists
3. **Data Refresh**: Stock prices updated via Yahoo Finance API
4. **News Fetching**: Recent news articles scraped from Google News
5. **Sentiment Analysis**: News headlines analyzed for market sentiment
6. **Display**: Aggregated data presented in dashboard with real-time updates

## External Dependencies

### APIs and Services
- **Yahoo Finance (yfinance)**: Real-time stock data, market metrics, and historical prices
- **Google News**: Web scraping for stock-related news articles
- **TextBlob**: Natural language processing for sentiment analysis

### Frontend Libraries
- **Bootstrap 5**: Responsive UI framework with dark theme
- **Font Awesome**: Icon library for enhanced UI
- **Chart.js**: Data visualization for portfolio charts

### Python Packages
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **BeautifulSoup**: Web scraping
- **Requests**: HTTP client
- **TextBlob**: Sentiment analysis

## Deployment Strategy

### Environment Configuration
- **Database**: Configurable via DATABASE_URL environment variable
- **Session Security**: SESSION_SECRET environment variable for production
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxy

### Application Setup
- **Database Initialization**: Automatic table creation on startup
- **Development Mode**: Debug mode enabled for development
- **Production Ready**: Configured for deployment with proper security headers

### Key Features
- **Auto-refresh**: Real-time data updates every 5 minutes
- **Error Handling**: Comprehensive logging and error recovery
- **Responsive Design**: Mobile-friendly interface
- **Performance**: Caching mechanisms for API data
- **Scalability**: Modular service architecture for easy expansion

The application follows a clean separation of concerns with dedicated services for external integrations, making it easy to maintain and extend with additional features like user authentication, advanced analytics, or additional data sources.