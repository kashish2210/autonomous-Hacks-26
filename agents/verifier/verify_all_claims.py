# verify_all_claims.py
from .agent import verify_claim
from agents.claim_extractor.claim_store import GlobalClaimStore


def verify_unverified_claims(store: GlobalClaimStore):
    for claim in store.unverified_claims():
        canonical = claim["canonical_claim"]
        print("Verifying: ", claim['canonical_claim'])

        try:
            result = verify_claim(canonical)

            store.update_verification(
                canonical_claim=canonical,
                verdict=result.verdict,
                confidence=result.confidence,
                reasoning=result.reasoning,
                evidence_sources=result.evidence_sources
            )

        except Exception as e:
            store.update_verification(
                canonical_claim=canonical,
                verdict="UNVERIFIABLE",
                confidence=0.0,
                reasoning=f"Verification failed: {str(e)}",
                evidence_sources=[]
            )
