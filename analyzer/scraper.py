import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time

class ArticleScraper:
    """Web scraper for extracting article content"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_article(self, url):
        """Scrape article from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_content(soup)
            
            if not content:
                return {
                    'success': False,
                    'error': 'Could not extract article content from this URL'
                }
            
            return {
                'success': True,
                'title': title,
                'content': content,
                'url': url
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Failed to fetch URL: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Scraping error: {str(e)}'
            }
    
    def _extract_title(self, soup):
        """Extract article title"""
        # Try multiple selectors
        selectors = [
            'h1',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'title'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                element = soup.select_one(selector)
                if element and element.get('content'):
                    return element['content']
            else:
                element = soup.select_one(selector)
                if element:
                    return element.get_text().strip()
        
        return 'Untitled Article'
    
    def _extract_content(self, soup):
        """Extract main article content"""
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            tag.decompose()
        
        # Try common article containers
        selectors = [
            'article',
            '[role="main"]',
            '.article-content',
            '.post-content',
            '.entry-content',
            'main'
        ]
        
        for selector in selectors:
            container = soup.select_one(selector)
            if container:
                paragraphs = container.find_all('p')
                if len(paragraphs) > 3:
                    text = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(text) > 200:
                        return text
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        text = '\n\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        return text if len(text) > 200 else None