# claim_store.py
from typing import Dict, List
from datetime import datetime


class GlobalClaimStore:
    def __init__(self):
        self.claims: Dict[str, dict] = {}

    def add_claim(self, claim: dict):
        key = claim["canonical_claim"]

        if key not in self.claims:
            self.claims[key] = {
                "canonical_claim": key,
                "occurrences": [],
                "verification": {
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
        if canonical_claim in self.claims:
            self.claims[canonical_claim]["verification"] = {
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": reasoning,
                "evidence_sources": evidence_sources,
                "verified_at": datetime.now().isoformat()
            }

    def unverified_claims(self):
        return [
            claim for claim in self.claims.values()
            if claim["verification"]["verdict"] is None
        ]

    def all(self):
        return list(self.claims.values())
