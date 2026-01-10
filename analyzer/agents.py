"""
Hybrid analyzer with API fallback to rule-based analysis
"""

import os
import re
from typing import Dict, List, TypedDict
from pydantic import BaseModel, Field
import json

# Try to import LangChain, but continue if not available
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate
    from langgraph.graph import StateGraph, END
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not available, using rule-based fallback")

# ============================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# ============================================

class NamedSource(BaseModel):
    """Model for a named source"""
    name: str = Field(description="Full name of the person or organization")
    title: str = Field(description="Position, role, or description")
    quote_context: str = Field(description="Context of their statement")
    credibility: str = Field(description="Credibility level: high, medium, or low")
    expertise_relevance: str = Field(description="How relevant their expertise is to the topic")

class AnonymousPhrase(BaseModel):
    """Model for anonymous attribution"""
    phrase: str = Field(description="The anonymous attribution phrase found")
    context: str = Field(description="Surrounding context of the phrase")
    vagueness_score: int = Field(description="Score 1-10, higher is more vague")

class RedFlag(BaseModel):
    """Model for journalism red flags"""
    severity: str = Field(description="HIGH, MEDIUM, or LOW")
    flag: str = Field(description="Name of the red flag")
    description: str = Field(description="Detailed description of the issue")
    recommendation: str = Field(description="How to improve this issue")

class BiasAnalysis(BaseModel):
    """Model for bias detection"""
    bias_type: str = Field(description="Type of bias detected")
    severity: str = Field(description="HIGH, MEDIUM, or LOW")
    evidence: str = Field(description="Evidence of the bias")
    context: str = Field(description="Where in the article this appears")

class SourceQualityMetrics(BaseModel):
    """Detailed source quality metrics"""
    diversity_score: float = Field(description="How diverse the sources are (0-100)")
    authority_score: float = Field(description="Authority level of sources (0-100)")
    independence_score: float = Field(description="Independence of sources (0-100)")
    transparency_score: float = Field(description="Overall transparency (0-100)")

class AnalysisState(TypedDict):
    """State that flows through the agent graph"""
    article_text: str
    article_metadata: Dict
    named_sources: List[NamedSource]
    anonymous_phrases: List[AnonymousPhrase]
    red_flags: List[RedFlag]
    bias_analysis: List[BiasAnalysis]
    source_quality: SourceQualityMetrics
    sentiment_analysis: Dict
    fact_check_suggestions: List[str]
    improvement_recommendations: List[str]
    final_score: float
    processing_steps: List[str]

# ============================================
# RULE-BASED FALLBACK ANALYZER
# ============================================

class RuleBasedAnalyzer:
    """Rule-based analyzer as fallback when API is unavailable"""
    
    def extract_named_sources(self, text: str) -> List[Dict]:
        """Extract named sources using regex patterns"""
        sources = []
        
        # Pattern 1: "Name, Title, said/stated"
        pattern1 = r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([^,]+?),\s*(?:said|stated|told|explained)'
        matches1 = re.finditer(pattern1, text)
        
        for match in matches1:
            name = match.group(1).strip()
            title = match.group(2).strip()
            # Get surrounding context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()
            
            sources.append({
                "name": name,
                "title": title,
                "quote_context": context[:150],
                "credibility": self._assess_credibility(title),
                "expertise_relevance": "Directly quoted in article"
            })
        
        # Pattern 2: "According to Name" or "Name said"
        pattern2 = r'(?:according to|said)\s+([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        matches2 = re.finditer(pattern2, text, re.IGNORECASE)
        
        for match in matches2:
            name = match.group(1).strip()
            if not any(s['name'] == name for s in sources):
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                sources.append({
                    "name": name,
                    "title": "Source",
                    "quote_context": context[:150],
                    "credibility": "medium",
                    "expertise_relevance": "Referenced in article"
                })
        
        return sources[:10]  # Limit to top 10
    
    def _assess_credibility(self, title: str) -> str:
        """Assess credibility based on title keywords"""
        title_lower = title.lower()
        
        high_cred_keywords = ['ceo', 'president', 'director', 'professor', 'dr.', 'expert', 'official', 'spokesperson']
        medium_cred_keywords = ['manager', 'analyst', 'researcher', 'representative', 'coordinator']
        
        for keyword in high_cred_keywords:
            if keyword in title_lower:
                return "high"
        
        for keyword in medium_cred_keywords:
            if keyword in title_lower:
                return "medium"
        
        return "low"
    
    def detect_anonymous_phrases(self, text: str) -> List[Dict]:
        """Detect anonymous attribution phrases"""
        phrases = []
        
        # Common anonymous patterns
        patterns = [
            (r'sources?\s+(?:say|said|claim|told|familiar)', 8),
            (r'officials?\s+(?:say|said|claim|told)', 7),
            (r'according to reports?', 9),
            (r'it is (?:believed|understood|reported)', 8),
            (r'(?:people|insiders?)\s+familiar with', 9),
            (r'allegedly', 7),
            (r'reportedly', 7),
            (r'anonymous\s+(?:source|official)', 10),
            (r'unnamed\s+(?:source|official)', 9),
            (r'experts?\s+(?:say|believe|suggest)', 5),
        ]
        
        for pattern, vagueness in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                phrases.append({
                    "phrase": match.group(0),
                    "context": context[:200],
                    "vagueness_score": vagueness
                })
        
        return phrases[:15]  # Limit to top 15
    
    def detect_bias(self, text: str, named_sources: List[Dict]) -> List[Dict]:
        """Detect potential bias indicators"""
        bias_list = []
        
        # Check for loaded language
        loaded_words = ['shocking', 'outrageous', 'devastating', 'incredible', 'unbelievable', 'stunning']
        for word in loaded_words:
            if re.search(rf'\b{word}\b', text, re.IGNORECASE):
                bias_list.append({
                    "bias_type": "Language Bias",
                    "severity": "MEDIUM",
                    "evidence": f"Use of loaded word: '{word}'",
                    "context": "Throughout article"
                })
                break
        
        # Check for one-sided sourcing
        if len(named_sources) > 0:
            titles = [s['title'].lower() for s in named_sources]
            if all('critic' in t or 'opponent' in t for t in titles):
                bias_list.append({
                    "bias_type": "Source Bias",
                    "severity": "HIGH",
                    "evidence": "All sources appear to be critics/opponents",
                    "context": "Named sources section"
                })
        
        return bias_list
    
    def identify_red_flags(self, named_count: int, anon_count: int, high_cred: int) -> List[Dict]:
        """Identify journalism red flags"""
        flags = []
        
        if named_count == 0:
            flags.append({
                "severity": "HIGH",
                "flag": "No Named Sources",
                "description": "Article contains no identifiable named sources",
                "recommendation": "Add at least 2-3 named, credible sources"
            })
        
        if named_count + anon_count == 1:
            flags.append({
                "severity": "HIGH",
                "flag": "Single Source Article",
                "description": "Article relies on only one source",
                "recommendation": "Seek multiple independent sources for verification"
            })
        
        if anon_count > named_count and named_count > 0:
            flags.append({
                "severity": "MEDIUM",
                "flag": "Excessive Anonymous Sources",
                "description": f"{anon_count} anonymous attributions vs {named_count} named sources",
                "recommendation": "Replace anonymous sources with named sources where possible"
            })
        
        if high_cred == 0 and named_count > 0:
            flags.append({
                "severity": "MEDIUM",
                "flag": "No High-Credibility Sources",
                "description": "No experts or officials with high credibility",
                "recommendation": "Include quotes from recognized experts or officials"
            })
        
        if anon_count > 10:
            flags.append({
                "severity": "HIGH",
                "flag": "Excessive Vague Attribution",
                "description": f"{anon_count} instances of anonymous/vague attribution",
                "recommendation": "Significantly reduce reliance on anonymous sources"
            })
        
        return flags

# ============================================
# ADVANCED ANALYZER WITH API FALLBACK
# ============================================

class AdvancedSourceAnalyzer:
    """Advanced analyzer that tries API first, falls back to rules"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.use_api = LANGCHAIN_AVAILABLE and self.api_key
        self.fallback = RuleBasedAnalyzer()
        
        if self.use_api:
            try:
                self.llm_analytical = ChatGroq(
                    api_key=self.api_key,
                    model="llama-3.3-70b-versatile",
                    temperature=0.0,
                    max_tokens=4000
                )
                print("✓ Using Groq API for analysis")
            except Exception as e:
                print(f"✗ Failed to initialize Groq API: {e}")
                self.use_api = False
        else:
            print("✓ Using rule-based fallback analysis")
    
    def analyze_article(self, article_text: str, metadata: Dict = None) -> Dict:
        """Run complete analysis"""
        
        print(f"\n{'='*60}")
        print(f"Starting analysis... (API: {self.use_api})")
        print(f"{'='*60}\n")
        
        # Extract named sources
        if self.use_api:
            named_sources = self._extract_sources_api(article_text)
        else:
            named_sources_data = self.fallback.extract_named_sources(article_text)
            named_sources = [NamedSource(**s) for s in named_sources_data]
        
        print(f"✓ Found {len(named_sources)} named sources")
        
        # Detect anonymous phrases
        if self.use_api:
            anonymous_phrases = self._detect_anonymous_api(article_text)
        else:
            anon_data = self.fallback.detect_anonymous_phrases(article_text)
            anonymous_phrases = [AnonymousPhrase(**p) for p in anon_data]
        
        print(f"✓ Found {len(anonymous_phrases)} anonymous phrases")
        
        # Detect bias
        if self.use_api:
            bias_analysis = []  # API version would go here
        else:
            bias_data = self.fallback.detect_bias(article_text, [s.dict() for s in named_sources])
            bias_analysis = [BiasAnalysis(**b) for b in bias_data]
        
        print(f"✓ Detected {len(bias_analysis)} bias instances")
        
        # Calculate metrics
        high_cred = sum(1 for s in named_sources if s.credibility == "high")
        
        # Identify red flags
        if self.use_api:
            red_flags_data = []  # API version would go here
        else:
            red_flags_data = self.fallback.identify_red_flags(
                len(named_sources),
                len(anonymous_phrases),
                high_cred
            )
        
        red_flags = [RedFlag(**f) for f in red_flags_data]
        print(f"✓ Identified {len(red_flags)} red flags")
        
        # Calculate quality metrics
        quality_metrics = self._calculate_metrics(
            named_sources, anonymous_phrases, red_flags, bias_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            len(named_sources), len(anonymous_phrases), high_cred, red_flags
        )
        
        final_score = quality_metrics.transparency_score
        
        print(f"\n{'='*60}")
        print(f"Final Transparency Score: {final_score}/100")
        print(f"{'='*60}\n")
        
        return {
            "named_sources": [s.dict() for s in named_sources],
            "anonymous_phrases": [p.dict() for p in anonymous_phrases],
            "red_flags": [f.dict() for f in red_flags],
            "bias_analysis": [b.dict() for b in bias_analysis],
            "source_quality": quality_metrics.dict(),
            "improvement_recommendations": recommendations,
            "final_score": final_score,
            "processing_steps": [
                f"Extracted {len(named_sources)} named sources",
                f"Found {len(anonymous_phrases)} anonymous phrases",
                f"Detected {len(bias_analysis)} bias instances",
                f"Identified {len(red_flags)} red flags",
                f"Final score: {final_score}/100"
            ],
            "source_breakdown": {
                "total_sources": len(named_sources) + len(anonymous_phrases),
                "named_count": len(named_sources),
                "anonymous_count": len(anonymous_phrases),
                "named_high_credibility": high_cred,
                "named_medium_credibility": sum(1 for s in named_sources if s.credibility == "medium"),
                "named_low_credibility": sum(1 for s in named_sources if s.credibility == "low"),
            },
            "transparency_score": final_score,
            "unique_source_count": len(named_sources) + len(anonymous_phrases)
        }
    
    def _extract_sources_api(self, text: str) -> List[NamedSource]:
        """Extract sources using API"""
        # Fallback to rule-based if API fails
        try:
            # API extraction code here
            return []
        except:
            named_sources_data = self.fallback.extract_named_sources(text)
            return [NamedSource(**s) for s in named_sources_data]
    
    def _detect_anonymous_api(self, text: str) -> List[AnonymousPhrase]:
        """Detect anonymous phrases using API"""
        try:
            # API detection code here
            return []
        except:
            anon_data = self.fallback.detect_anonymous_phrases(text)
            return [AnonymousPhrase(**p) for p in anon_data]
    
    def _calculate_metrics(self, named_sources, anonymous_phrases, red_flags, bias_analysis) -> SourceQualityMetrics:
        """Calculate quality metrics"""
        
        # DIVERSITY SCORE
        diversity_score = 50.0
        unique_orgs = len(set(s.title for s in named_sources))
        if unique_orgs >= 5:
            diversity_score += 30
        elif unique_orgs >= 3:
            diversity_score += 15
        
        if len(bias_analysis) == 0:
            diversity_score += 20
        else:
            diversity_score -= len(bias_analysis) * 10
        
        diversity_score = max(0, min(100, diversity_score))
        
        # AUTHORITY SCORE
        authority_score = 50.0
        high_cred = sum(1 for s in named_sources if s.credibility == "high")
        low_cred = sum(1 for s in named_sources if s.credibility == "low")
        
        authority_score += high_cred * 15
        authority_score -= low_cred * 10
        authority_score = max(0, min(100, authority_score))
        
        # INDEPENDENCE SCORE
        independence_score = 100.0
        total = len(named_sources) + len(anonymous_phrases)
        if total > 0:
            anon_ratio = len(anonymous_phrases) / total
            independence_score -= anon_ratio * 60
        
        high_vague = sum(1 for p in anonymous_phrases if p.vagueness_score >= 7)
        independence_score -= high_vague * 8
        independence_score = max(0, min(100, independence_score))
        
        # TRANSPARENCY SCORE
        transparency_score = 70.0
        
        if len(named_sources) == 0:
            transparency_score = 10.0
        else:
            transparency_score += min(len(named_sources) * 6, 25)
        
        if total == 1:
            transparency_score -= 40
        elif total == 2:
            transparency_score -= 20
        
        for flag in red_flags:
            if flag.severity == "HIGH":
                transparency_score -= 15
            elif flag.severity == "MEDIUM":
                transparency_score -= 10
            else:
                transparency_score -= 5
        
        transparency_score = max(0, min(100, transparency_score))
        
        return SourceQualityMetrics(
            diversity_score=round(diversity_score, 1),
            authority_score=round(authority_score, 1),
            independence_score=round(independence_score, 1),
            transparency_score=round(transparency_score, 1)
        )
    
    def _generate_recommendations(self, named_count, anon_count, high_cred, red_flags) -> List[str]:
        """Generate improvement recommendations"""
        recs = []
        
        if named_count == 0:
            recs.append("Add at least 2-3 named, credible sources to the article")
        elif named_count < 3:
            recs.append(f"Increase named sources from {named_count} to at least 3-4 for better credibility")
        
        if anon_count > 5:
            recs.append(f"Reduce anonymous attributions from {anon_count} - try to get sources on the record")
        
        if high_cred == 0:
            recs.append("Include quotes from recognized experts or officials in the field")
        
        if named_count + anon_count < 3:
            recs.append("Seek additional independent sources to verify claims")
        
        if anon_count > named_count:
            recs.append("Balance the article by replacing anonymous sources with named sources where possible")
        
        if len(recs) == 0:
            recs.append("Good journalism! Consider adding diverse perspectives to strengthen the article further")
        
        return recs[:5]