# web_search_helper.py
"""
Helper module for performing web searches using Google Custom Search API
You'll need to set up Google Custom Search API and get API credentials
"""
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class WebSearchHelper:
    """Helper class for performing web searches"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Perform a Google search and return formatted results
        
        Args:
            query: Search query string
            num_results: Number of results to return (max 10)
            
        Returns:
            List of search result dictionaries with title, url, snippet
        """
        if not self.api_key or not self.search_engine_id:
            print("Warning: Google API credentials not configured")
            return self._get_mock_results(query)
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return self._get_mock_results(query)
    
    def multi_search(self, queries: List[str], results_per_query: int = 3) -> List[Dict]:
        """
        Perform multiple searches and aggregate results
        
        Args:
            queries: List of search queries
            results_per_query: Number of results per query
            
        Returns:
            Aggregated list of search results
        """
        all_results = []
        seen_urls = set()
        
        for query in queries:
            results = self.search(query, results_per_query)
            
            # Deduplicate by URL
            for result in results:
                url = result['url']
                if url not in seen_urls:
                    all_results.append(result)
                    seen_urls.add(url)
        
        return all_results
    
    def _get_mock_results(self, query: str) -> List[Dict]:
        """
        Return mock search results for testing when API is not configured
        """
        return [
            {
                'title': f'Mock Result 1 for: {query}',
                'url': 'https://example.com/result1',
                'snippet': 'This is a mock search result snippet for testing purposes. In production, this would contain actual search results from Google.'
            },
            {
                'title': f'Mock Result 2 for: {query}',
                'url': 'https://example.com/result2',
                'snippet': 'Another mock result. Please configure GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID in your .env file for real searches.'
            },
            {
                'title': f'Mock Result 3 for: {query}',
                'url': 'https://example.com/result3',
                'snippet': 'Third mock result demonstrating the format. Real searches would return relevant web pages matching the query.'
            }
        ]


# Standalone search function for easy import
def perform_web_search(query: str, num_results: int = 5) -> List[Dict]:
    """
    Convenience function to perform a web search
    
    Usage:
        from web_search_helper import perform_web_search
        results = perform_web_search("Python programming tutorial")
    """
    helper = WebSearchHelper()
    return helper.search(query, num_results)


def perform_multi_search(queries: List[str], results_per_query: int = 3) -> List[Dict]:
    """
    Convenience function to perform multiple searches
    
    Usage:
        from web_search_helper import perform_multi_search
        results = perform_multi_search(["query 1", "query 2"])
    """
    helper = WebSearchHelper()
    return helper.multi_search(queries, results_per_query)


# Example usage
if __name__ == "__main__":
    # Test single search
    print("Testing single search:")
    results = perform_web_search("artificial intelligence latest news")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Snippet: {result['snippet'][:100]}...")
    
    # Test multiple searches
    print("\n\nTesting multiple searches:")
    results = perform_multi_search([
        "machine learning tutorials",
        "deep learning frameworks"
    ], results_per_query=2)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")