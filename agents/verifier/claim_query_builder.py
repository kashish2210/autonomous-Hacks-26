# claim_query_builder.py

def claim_to_search_queries(canonical_claim: str, context: str = "") -> list[str]:
    """
    Converts canonical claim into search-friendly queries.
    
    Args:
        canonical_claim: The claim in format "subject|predicate|object|time|location|source"
        context: Optional context to add to queries (e.g., "Iran protests")
    """
    subject, predicate, obj, time, location, source = canonical_claim.split("|")

    queries = []

    # Build base query from non-null components
    components = []
    
    if subject != "null":
        components.append(subject.replace('_', ' '))
    if predicate != "null":
        components.append(predicate.replace('_', ' '))
    if obj != "null":
        components.append(obj.replace('_', ' '))
    if time != "null":
        components.append(time.replace('_', ' '))
    if location != "null":
        components.append(location.replace('_', ' '))
    
    base = " ".join(components)
    
    # Add context if provided (helps with ambiguous queries)
    if context:
        queries.append(f"{context} {base}")
    else:
        queries.append(base)

    # Location-specific query
    if location != "null" and location != "":
        location_query = f"{location.replace('_', ' ')} {predicate.replace('_', ' ')} {obj.replace('_', ' ')}"
        if context:
            location_query = f"{context} {location_query}"
        queries.append(location_query)

    # Time-specific query
    if time != "null" and time != "":
        time_query = f"{time.replace('_', ' ')} {location.replace('_', ' ')} {predicate.replace('_', ' ')}"
        if context:
            time_query = f"{context} {time_query}"
        queries.append(time_query)

    # Source-based query
    if source != "null" and source != "":
        source_query = f"{source.replace('_', ' ')} {obj.replace('_', ' ')}"
        queries.append(source_query)

    # Remove duplicates and empty queries
    queries = list(dict.fromkeys([q.strip() for q in queries if q.strip()]))
    
    return queries