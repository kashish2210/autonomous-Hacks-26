#claim_store.py (Enhanced version with verification support)
from typing import Dict, List, Optional
from datetime import datetime


class GlobalClaimStore:
    """Enhanced claim store with verification tracking"""
    
    def __init__(self):
        self.claims: Dict[str, dict] = {}
    
    def add_claim(self, claim: dict):
        """Add a claim to the store"""
        key = claim["canonical_claim"]
        
        if key not in self.claims:
            self.claims[key] = {
                "canonical_claim": key,
                "occurrences": [],
                "verification": {
                    "is_verified": False,
                    "verdict": None,
                    "confidence": None,
                    "reasoning": None,
                    "evidence_sources": [],
                    "verified_at": None
                }
            }
        
        self.claims[key]["occurrences"].append({
            "sentence_id": claim["sentence_id"],
            "paragraph_index": claim["paragraph_index"],
            "original_sentence": claim["original_sentence"]
        })
    
    def update_verification(
        self, 
        canonical_claim: str, 
        verdict: str,
        confidence: float,
        reasoning: str,
        evidence_sources: List[str]
    ):
        """Update verification status for a claim"""
        if canonical_claim in self.claims:
            self.claims[canonical_claim]["verification"] = {
                "is_verified": verdict == "VERIFIED",
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": reasoning,
                "evidence_sources": evidence_sources,
                "verified_at": datetime.now().isoformat()
            }
    
    def get_claim(self, canonical_claim: str) -> Optional[dict]:
        """Get a specific claim by its canonical form"""
        return self.claims.get(canonical_claim)
    
    def all(self) -> List[dict]:
        """Return all claims"""
        return list(self.claims.values())
    
    def unverified_claims(self) -> List[dict]:
        """Return only unverified claims"""
        return [
            claim for claim in self.claims.values()
            if not claim["verification"]["is_verified"]
        ]
    
    def verified_claims(self) -> List[dict]:
        """Return only verified claims"""
        return [
            claim for claim in self.claims.values()
            if claim["verification"]["verdict"] == "VERIFIED"
        ]
    
    def get_verification_summary(self) -> dict:
        """Get summary statistics of verification"""
        total = len(self.claims)
        verified = len([c for c in self.claims.values() 
                       if c["verification"]["verdict"] == "VERIFIED"])
        false = len([c for c in self.claims.values() 
                    if c["verification"]["verdict"] == "FALSE"])
        unverifiable = len([c for c in self.claims.values() 
                           if c["verification"]["verdict"] == "UNVERIFIABLE"])
        partially = len([c for c in self.claims.values() 
                        if c["verification"]["verdict"] == "PARTIALLY_VERIFIED"])
        pending = len([c for c in self.claims.values() 
                      if c["verification"]["verdict"] is None])
        
        return {
            "total": total,
            "verified": verified,
            "false": false,
            "unverifiable": unverifiable,
            "partially_verified": partially,
            "pending": pending
        }