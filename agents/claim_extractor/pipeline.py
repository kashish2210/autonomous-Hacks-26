#pipeline.py
from .sentence_segmentation import sentence_segmentation
from .sentence_classifier import classify_sentence
from .claim_normalizer import normalize_claim
from .claim_store import GlobalClaimStore
from dotenv import load_dotenv

load_dotenv()
def run_pipeline(text: str):
    sentences = sentence_segmentation(text)
    store = GlobalClaimStore()

    for sentence in sentences:
        sentence = classify_sentence(sentence)

        normalized = normalize_claim(sentence)
        if normalized:
            store.add_claim(normalized)

    return {
        "sentences": sentences,
        "claims": store.all()
    }


if __name__ == "__main__":
    article = """
    The finance minister said the economy grew by 7.2% last year.
    However, experts disputed the figures.

    BREAKING: Fire breaks out in Mumbai.
    Rescue operations underway.
    """

    result = run_pipeline(article)

    print("CLAIMS:")
    for c in result["claims"]:
        print(c)
