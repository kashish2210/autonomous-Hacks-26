# claim_query_builder.py

def claim_to_search_queries(canonical_claim: str) -> list[str]:
    """
    Converts canonical claim into Google-friendly queries.
    """
    subject, predicate, obj, time, location, source = canonical_claim.split("|")

    queries = []

    base = " ".join(
        x for x in [subject, predicate, obj] if x != "null"
    )

    if time != "null":
        base += f" {time.replace('_', ' ')}"

    if location != "null":
        base += f" {location.replace('_', ' ')}"

    queries.append(base)

    # Authority-based query
    if source != "null":
        queries.append(f"{source.replace('_', ' ')} {obj}")

    return queries
