import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import urllib.parse
import time

logger = logging.getLogger(__name__)

class NewsService:
    """Service for scraping news from Google News"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_stock_news(self, symbol, limit=10):
        """Get news articles for a specific stock symbol"""
        try:
            # Search query for the stock
            query = f"{symbol} stock news"
            encoded_query = urllib.parse.quote(query)
            
            # Google News URL
            url = f"https://news.google.com/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            article_elements = soup.find_all('article')
            
            for article in article_elements[:limit]:
                try:
                    # Extract title
                    title_elem = article.find('h3') or article.find('h4')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue
                    
                    # Extract link
                    link_elem = article.find('a')
                    url = None
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('./'):
                            url = f"https://news.google.com{href[1:]}"
                        elif href.startswith('/'):
                            url = f"https://news.google.com{href}"
                        else:
                            url = href
                    
                    # Extract source and time
                    source = "Google News"
                    time_elem = article.find('time')
                    published_date = datetime.now()
                    
                    if time_elem:
                        try:
                            # Try to parse the datetime attribute
                            datetime_attr = time_elem.get('datetime')
                            if datetime_attr:
                                published_date = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        except:
                            pass
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'source': source,
                        'published_date': published_date,
                        'symbol': symbol
                    })
                
                except Exception as e:
                    logger.error(f"Error parsing article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []
    
    def get_general_market_news(self, limit=10):
        """Get general market news"""
        try:
            query = "stock market news"
            encoded_query = urllib.parse.quote(query)
            
            url = f"https://news.google.com/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            article_elements = soup.find_all('article')
            
            for article in article_elements[:limit]:
                try:
                    title_elem = article.find('h3') or article.find('h4')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if not title:
                        continue
                    
                    link_elem = article.find('a')
                    url = None
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href')
                        if href.startswith('./'):
                            url = f"https://news.google.com{href[1:]}"
                        elif href.startswith('/'):
                            url = f"https://news.google.com{href}"
                        else:
                            url = href
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'source': "Google News",
                        'published_date': datetime.now(),
                        'symbol': 'MARKET'
                    })
                
                except Exception as e:
                    logger.error(f"Error parsing market news article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching market news: {e}")
            return []
    
    def get_multiple_stocks_news(self, symbols, limit_per_stock=5):
        """Get news for multiple stocks"""
        all_news = []
        
        for symbol in symbols:
            try:
                news = self.get_stock_news(symbol, limit_per_stock)
                all_news.extend(news)
                # Add delay to avoid rate limiting
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error fetching news for {symbol}: {e}")
                continue
        
        # Sort by date
        all_news.sort(key=lambda x: x.get('published_date', datetime.now()), reverse=True)
        
        return all_news
    
    def extract_article_content(self, url):
        """Extract full article content from URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find article content
            content = ""
            
            # Common article content selectors
            selectors = [
                'article',
                '.article-content',
                '.story-body',
                '.entry-content',
                '.post-content',
                '.content',
                'main'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    break
            
            if not content:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    content = body.get_text(strip=True)
            
            return content[:2000]  # Limit content length
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""
