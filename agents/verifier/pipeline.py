from agents.claim_extractor.pipeline import run_pipeline
from agents.verifier.verify_all_claims import verify_unverified_claims
from dotenv import load_dotenv

def verifier_run_pipeline(text: str):
    store = run_pipeline(text)

    verify_unverified_claims(store)
    return store.all()


if __name__ == "__main__":
    verifier_run_pipeline("""The finance minister said the economy grew by 7.2% last year.
    However, experts disputed the figures.

    BREAKING: Fire breaks out in Mumbai.
    Rescue operations underway.""")