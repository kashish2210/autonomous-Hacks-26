# search_tool.py
from duckduckgo_search import DDGS
from dotenv import load_dotenv
import os
import time
import re

load_dotenv()

class SearchWrapper:
    """
    DuckDuckGo search wrapper with robust query handling and language filtering
    """
    def __init__(self, params=None):
        self.params = params or {}
        self.max_results = self.params.get('num', 10)  # Get more, filter to 5
        print("=" * 50)
        print("INFO: Using DuckDuckGo Search (Free, No API Key Required)")
        print(f"INFO: Max results per query = {self.max_results}")
        print("=" * 50)
    
    def extract_claim_parts(self, query):
        """
        Extract meaningful parts from structured claim format
        Input: "greenland_mp_kuno_fencker|say|mineral-rich island is not for sale|null|greenland"
        Output: {
            'entity': 'Kuno Fencker',
            'action': 'say',
            'claim': 'mineral-rich island is not for sale',
            'topic': 'greenland'
        }
        """
        parts = query.split('|')
        
        result = {
            'entity': '',
            'action': '',
            'claim': '',
            'topic': ''
        }
        
        if len(parts) >= 3:
            # Extract entity (convert greenland_mp_kuno_fencker -> Kuno Fencker)
            entity_raw = parts[0]
            entity_words = entity_raw.replace('_', ' ').split()
            # Keep only capitalized words or last 2-3 words as name
            entity_cleaned = ' '.join([w.capitalize() for w in entity_words if len(w) > 2])
            result['entity'] = entity_cleaned
            
            # Extract action
            result['action'] = parts[1] if parts[1] != 'null' else ''
            
            # Extract main claim
            result['claim'] = parts[2] if parts[2] != 'null' else ''
            
            # Extract topic
            if len(parts) > 4:
                result['topic'] = parts[4] if parts[4] != 'null' else ''
        
        return result
    
    def construct_search_queries(self, query):
        """
        Create multiple optimized search queries from the input
        Returns a list of queries to try in order
        """
        queries = []
        
        # Parse the structured claim
        claim_parts = self.extract_claim_parts(query)
        
        # The claim text is the MOST IMPORTANT - it should be the primary search term
        if claim_parts['claim']:
            # Strategy 1: Entity + action + claim (most specific)
            if claim_parts['entity'] and claim_parts['action']:
                # "earth atmosphere" + "compose" + "nitrogen oxygen" 
                action_clean = claim_parts['action'].replace('-', ' ')
                queries.append(f"{claim_parts['entity']} {action_clean} {claim_parts['claim']}")
            
            # Strategy 2: Just claim text (most direct)
            queries.append(claim_parts['claim'])
            
            # Strategy 3: Claim + topic
            if claim_parts['topic']:
                queries.append(f"{claim_parts['claim']} {claim_parts['topic']}")
            
            # Strategy 4: Entity + claim
            if claim_parts['entity']:
                queries.append(f"{claim_parts['entity']} {claim_parts['claim']}")
        
        # Strategy 5: Topic + entity + action
        if claim_parts['topic'] and claim_parts['entity']:
            queries.append(f"{claim_parts['entity']} {claim_parts['topic']}")
        
        # Strategy 6: Just entity if we have it
        if claim_parts['entity']:
            queries.append(claim_parts['entity'])
        
        # Clean the original query as fallback
        cleaned = query.replace('|', ' ').replace('_', ' ')
        cleaned = ' '.join([w for w in cleaned.split() if w.lower() != 'null' and len(w) > 2])
        if cleaned and cleaned not in queries:
            queries.append(cleaned)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            q_lower = q.lower().strip()
            if q_lower and q_lower not in seen:
                seen.add(q_lower)
                unique_queries.append(q)
        
        print(f"   🔍 Search strategies: {unique_queries[:3]}")
        return unique_queries[:3]  # Return top 3 strategies

    def is_english_result(self, result):
        """
        STRICT English-only check
        Returns True only if content is in English with Latin alphabet
        """
        title = result.get('title', '')
        snippet = result.get('body', '')
        url = result.get('link', '')
        combined = title + ' ' + snippet
        
        # Reject if empty
        if not combined.strip():
            return False
        
        # STRICT: Reject any CJK (Chinese, Japanese, Korean) characters
        if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', combined):
            return False
        
        # STRICT: Reject any Cyrillic characters
        if re.search(r'[\u0400-\u04ff]', combined):
            return False
        
        # STRICT: Reject any Arabic/Hebrew characters
        if re.search(r'[\u0600-\u06ff\u0590-\u05ff]', combined):
            return False
        
        # Reject Chinese domains (zhihu, baidu, etc.)
        chinese_domains = ['zhihu.com', 'baidu.com', 'qq.com', 'sina.com', 'weibo.com']
        if any(domain in url.lower() for domain in chinese_domains):
            return False
        
        # Count total non-ASCII characters
        non_ascii = len(re.findall(r'[^\x00-\x7F]', combined))
        total_chars = len(combined)
        
        # STRICT: Reject if more than 10% non-ASCII (was 20%)
        if total_chars > 0:
            non_ascii_ratio = non_ascii / total_chars
            if non_ascii_ratio > 0.10:
                return False
        
        return True
    
    def filter_english_results(self, results):
        """
        AGGRESSIVELY filter results to ONLY include English content
        Rejects any non-English or mixed-language content
        """
        english_results = []
        rejected_count = 0
        
        for r in results:
            if self.is_english_result(r):
                english_results.append(r)
            else:
                rejected_count += 1
                # Log rejected sources for debugging
                rejected_title = r.get('title', 'Unknown')
                print(f"   ❌ Rejected (non-English): {rejected_title[:50]}...")
        
        print(f"   ✅ Filtered: {len(results)} total → {len(english_results)} English (rejected {rejected_count})")
        
        return english_results
    
    def check_relevance(self, results, query):
        """
        Check if results are relevant to the query
        """
        if not results:
            return False
        
        # Extract key terms (words longer than 3 chars, excluding common words)
        stop_words = {'the', 'and', 'for', 'not', 'with', 'from', 'that', 'this', 'said', 'says'}
        query_terms = [
            word.lower() 
            for word in query.split() 
            if len(word) > 3 and word.lower() not in stop_words
        ]
        
        if not query_terms:
            return True  # If no key terms, accept results
        
        relevant_count = 0
        for result in results[:3]:
            title = result.get('title', '').lower()
            snippet = result.get('body', '').lower()
            combined = title + ' ' + snippet
            
            # Check if at least 1 key term appears
            matches = sum(1 for term in query_terms if term in combined)
            if matches > 0:
                relevant_count += 1
        
        # At least 1 of top 3 should be relevant
        return relevant_count >= 1

    def run(self, query, attempt=1, max_attempts=3):
        """
        Run search with automatic query optimization and fallback
        ALWAYS forces English-only results
        """
        # Get search queries to try
        search_queries = self.construct_search_queries(query)
        
        if attempt > len(search_queries):
            return "No relevant results found after trying multiple search strategies."
        
        current_query = search_queries[attempt - 1]
        
        # FORCE ENGLISH: Add "english" or "news" to query if not present
        if 'english' not in current_query.lower() and len(current_query.split()) < 8:
            current_query = current_query + " news"
        
        print(f"\n🔍 Attempt {attempt}/{len(search_queries)} - Searching: '{current_query}'")
        
        try:
            with DDGS() as ddgs:
                # FORCE ENGLISH-ONLY configurations
                # Using backend parameter 'l=en' equivalent through region settings
                search_configs = [
                    {'region': 'us-en', 'timelimit': 'm', 'backend': 'api'},   # US English, last month
                    {'region': 'uk-en', 'timelimit': 'w', 'backend': 'api'},   # UK English, last week
                    {'region': 'us-en', 'timelimit': None, 'backend': 'api'},  # US English, all time
                ]
                
                config = search_configs[min(attempt - 1, len(search_configs) - 1)]
                
                results = list(ddgs.text(
                    current_query,
                    region=config['region'],
                    safesearch='moderate',
                    timelimit=config['timelimit'],
                    max_results=self.max_results * 2  # Get 2x results to filter more aggressively
                ))
            
            # Filter to English only - STRICT FILTERING
            english_results = self.filter_english_results(results)
            
            # If we got zero English results, immediately try next strategy
            if not english_results:
                print(f"⚠️ Zero English results found. Trying next strategy...")
                if attempt < len(search_queries):
                    time.sleep(0.5)
                    return self.run(query, attempt + 1, max_attempts)
                else:
                    return "Unable to find any English-language results. The topic may not have English coverage, or try rephrasing your query."
            
            # Check relevance of English results
            if self.check_relevance(english_results, current_query):
                # SUCCESS: Got relevant English results
                final_results = english_results[:5]
                formatted = self.format_results(final_results)
                print(f"✅ SUCCESS: {len(final_results)} relevant English results\n")
                return formatted
            
            # Got English results but not relevant - try next query
            if attempt < len(search_queries):
                print(f"⚠️ English results found but not relevant. Trying next strategy...")
                time.sleep(0.5)
                return self.run(query, attempt + 1, max_attempts)
            else:
                # Last attempt - return what we have
                print(f"⚠️ Returning best available English results (may not be perfectly relevant)")
                return self.format_results(english_results[:5])
                
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            print(f"❌ {error_msg}")
            
            # Try next query on error
            if attempt < len(search_queries):
                print(f"🔄 Retrying with next strategy...")
                time.sleep(1)
                return self.run(query, attempt + 1, max_attempts)
            
            return error_msg
    
    def format_results(self, results):
        """Format search results as string"""
        formatted_output = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            link = result.get('link', '')
            snippet = result.get('body', 'No description')
            
            # Truncate snippet if too long
            if len(snippet) > 300:
                snippet = snippet[:297] + "..."
            
            formatted_output.append(f"{i}. {title}\n   {snippet}\n   URL: {link}")
        
        output = "\n\n".join(formatted_output)
        print(f"   📄 Formatted results: {len(output)} chars from {len(results)} sources")
        return output

    def results(self, query):
        """Returns structured results (for compatibility)"""
        search_queries = self.construct_search_queries(query)
        
        for search_query in search_queries:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(
                        search_query,
                        region='wt-wt',
                        safesearch='moderate',
                        timelimit='m',
                        max_results=self.max_results
                    ))
                    
                    # Filter to English
                    english_results = self.filter_english_results(results)
                    
                    if english_results:
                        return english_results[:5]
                        
            except Exception as e:
                print(f"Search error: {e}")
                continue
        
        return []


# Create the search instance
search = SearchWrapper(params={"num": 10})


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING IMPROVED SEARCH")
    print("="*80)
    
    test_queries = [
        "greenland_mp_kuno_fencker|say|mineral-rich island is not for sale|null|greenland|greenland_mp_kuno_fencker",
        "Trump|want|buy Greenland|2025|USA|Trump",
    ]
    
    for test_query in test_queries:
        print(f"\n{'='*80}")
        print(f"Testing: {test_query}")
        print(f"{'='*80}")
        
        result = search.run(test_query)
        
        print(f"\n{'='*80}")
        print("RESULTS:")
        print(f"{'='*80}")
        print(result)
        print("\n")