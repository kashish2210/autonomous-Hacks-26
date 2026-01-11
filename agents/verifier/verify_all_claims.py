# verify_all_claims.py
from .agent import verify_claim
from agents.claim_extractor.claim_store import GlobalClaimStore


def verify_unverified_claims(store: GlobalClaimStore):
    unverified = store.unverified_claims()
    print(f"\n📋 Found {len(unverified)} unverified claims to check")
    
    for i, claim in enumerate(unverified, 1):
        canonical = claim["canonical_claim"]
        print(f"\n[{i}/{len(unverified)}] Verifying: {canonical}")

        try:
            result = verify_claim(canonical)

            store.update_verification(
                canonical_claim=canonical,
                verdict=result.verdict,
                confidence=result.confidence,
                reasoning=result.reasoning,
                evidence_sources=result.evidence_sources
            )
            print(f"    → Result: {result.verdict} (confidence: {result.confidence})")

        except Exception as e:
            print(f"    ✗ Error: {str(e)}")
            store.update_verification(
                canonical_claim=canonical,
                verdict="UNVERIFIABLE",
                confidence=0.0,
                reasoning=f"Verification failed: {str(e)}",
                evidence_sources=[]
            )
