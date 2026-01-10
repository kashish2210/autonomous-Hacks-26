"""
Fact Verification Agent using LangChain with Groq and Web Search
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


class VerificationResult(BaseModel):
    """Structured verification result"""
    verdict: Literal["VERIFIED", "FALSE", "UNVERIFIABLE", "PARTIALLY_VERIFIED"] = Field(
        description="Final verification verdict"
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(
        description="Explanation of the verification decision"
    )
    evidence_sources: List[str] = Field(
        default_factory=list,
        description="URLs or sources that support the verdict"
    )


class FactVerifierAgent:
    """
    Agent that verifies factual claims using web search
    """
    
    def __init__(self):
        self.llm = llm
        self.search_prompt = ChatPromptTemplate.from_template("""
You are a fact-checking assistant. Generate 2-3 precise Google search queries 
to verify the following claim.

Claim: {claim}

Return ONLY a JSON array of search queries, nothing else.
Example: ["query 1", "query 2", "query 3"]
""")
        
        self.verification_prompt = ChatPromptTemplate.from_template("""
You are a professional fact-checker. Analyze the claim against search results.

CLAIM:
{claim}

SEARCH RESULTS:
{search_results}

Evaluate the claim and provide:
1. Verdict: VERIFIED (claim is accurate), FALSE (claim is inaccurate), 
   UNVERIFIABLE (insufficient evidence), PARTIALLY_VERIFIED (partially true)
2. Confidence: 0.0 to 1.0
3. Reasoning: Brief explanation (2-3 sentences)
4. Evidence sources: List of URLs that support your verdict

Return ONLY valid JSON in this exact format:
{{
    "verdict": "VERIFIED",
    "confidence": 0.95,
    "reasoning": "Your reasoning here",
    "evidence_sources": ["url1", "url2"]
}}
""")
        
        self.search_chain = self.search_prompt | self.llm | StrOutputParser()
        self.verification_chain = self.verification_prompt | self.llm | StrOutputParser()
    
    def _generate_search_queries(self, claim: str) -> List[str]:
        """Generate search queries for the claim"""
        try:
            result = self.search_chain.invoke({"claim": claim})
            # Parse JSON array
            queries = json.loads(result)
            return queries[:3]  # Limit to 3 queries
        except Exception as e:
            print(f"Error generating queries: {e}")
            # Fallback to simple query
            return [claim]
    
    def _perform_web_search(self, query: str, max_results: int = 3) -> List[dict]:
        """
        Perform web search using the web_search tool
        Returns list of search results
        """
        # This will be called from Django view with actual web_search results
        # Placeholder for now
        return []
    
    def _format_search_results(self, all_results: List[dict]) -> str:
        """Format search results for the LLM"""
        formatted = []
        for i, result in enumerate(all_results, 1):
            formatted.append(f"""
Result {i}:
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Snippet: {result.get('snippet', 'N/A')}
---
""")
        return "\n".join(formatted)
    
    def verify_claim(self, claim: str, search_results: List[dict]) -> VerificationResult:
        """
        Verify a claim using provided search results
        
        Args:
            claim: The claim to verify
            search_results: List of search result dicts from web_search
            
        Returns:
            VerificationResult with verdict, confidence, reasoning, and sources
        """
        try:
            # Format search results
            formatted_results = self._format_search_results(search_results)
            
            # Get verification from LLM
            result = self.verification_chain.invoke({
                "claim": claim,
                "search_results": formatted_results
            })
            
            # Parse JSON response
            result_dict = json.loads(result)
            
            return VerificationResult(**result_dict)
            
        except Exception as e:
            print(f"Error during verification: {e}")
            return VerificationResult(
                verdict="UNVERIFIABLE",
                confidence=0.0,
                reasoning=f"Verification failed due to error: {str(e)}",
                evidence_sources=[]
            )
    
    def get_search_queries(self, claim: str) -> List[str]:
        """Public method to get search queries for a claim"""
        return self._generate_search_queries(claim)


# Example usage and testing
if __name__ == "__main__":
    agent = FactVerifierAgent()
    
    # Test claim
    test_claim = "finance_minister|state|economy_grew_by_7.2%|last_year|null|null"
    
    # Generate search queries
    queries = agent.get_search_queries(test_claim)
    print("Search Queries:", queries)
    
    # Mock search results for testing
    mock_results = [
        {
            "title": "Economy Growth Report 2023",
            "url": "https://example.com/economy-report",
            "snippet": "The finance minister announced that the economy grew by 7.2% last year..."
        },
        {
            "title": "Economic Analysis",
            "url": "https://example.com/analysis",
            "snippet": "Independent analysis confirms GDP growth of approximately 7.1-7.3% in the previous fiscal year..."
        }
    ]
    
    # Verify claim
    result = agent.verify_claim(test_claim, mock_results)
    print(f"\nVerdict: {result.verdict}")
    print(f"Confidence: {result.confidence}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Sources: {result.evidence_sources}")