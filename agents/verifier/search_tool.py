# search_tool.py
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

class SearchWrapper:
    """
    DuckDuckGo search wrapper that mimics SerpAPIWrapper interface
    """
    def __init__(self, params=None):
        self.params = params or {}
        self.max_results = self.params.get('num', 5)
        print("=" * 50)
        print("INFO: Using DuckDuckGo Search (Free, No API Key Required)")
        print(f"INFO: Max results per query = {self.max_results}")
        print("=" * 50)
    
    def run(self, query):
        """
        Run search query and return results as a formatted string
        """
        print(f"\n🔍 Searching for: {query}")
        
        try:
            with DDGS() as ddgs:
                # Use timelimit for recent results, region for English content
                results = list(ddgs.text(
                    query,
                    region='us-en',      # US English results
                    safesearch='off',     # Allow all content
                    timelimit=None,       # No time limit (search all time)
                    max_results=self.max_results
                ))
                
                if not results:
                    return "No results found."
                
                # Format results
                formatted_output = []
                for i, result in enumerate(results, 1):
                    title = result.get('title', 'No title')
                    link = result.get('link', '')
                    snippet = result.get('body', 'No description')
                    
                    formatted_output.append(f"{i}. {title}\n   {snippet}\n   URL: {link}")
                
                output = "\n\n".join(formatted_output)
                print(f"✅ Found {len(results)} results\n")
                return output
                
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def results(self, query):
        """Returns structured results"""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    region='us-en',
                    safesearch='off',
                    max_results=self.max_results
                ))
                return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

# Create the search instance
search = SearchWrapper(params={"num": 5})