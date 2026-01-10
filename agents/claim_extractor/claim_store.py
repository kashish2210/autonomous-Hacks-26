class GlobalClaimStore:
    def __init__(self):
        self.claims = {}

    def add_claim(self, claim: dict):
        key = claim["canonical_claim"]

        if key not in self.claims:
            self.claims[key] = {
                "canonical_claim": key,
                "occurrences": []
            }

        self.claims[key]["occurrences"].append({
            "sentence_id": claim["sentence_id"],
            "paragraph_index": claim["paragraph_index"],
            "original_sentence": claim["original_sentence"]
        })

    def all(self):
        return list(self.claims.values())
