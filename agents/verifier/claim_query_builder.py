# claim_query_builder.py

def claim_to_search_queries(canonical_claim: str, context: str = "") -> list[str]:
    """
    Converts canonical claim into SHORT, search-optimized queries.
    
    Args:
        canonical_claim: "subject|predicate|object|time|location|source"
        context: Optional context prefix
    """
    parts = canonical_claim.split("|")
    subject, predicate, obj, time, location, source = [
        p.replace('_', ' ').strip() if p != "null" else "" 
        for p in parts
    ]
    
    queries = []
    
    # Extract key numbers/facts from object (e.g., "13,000 miles")
    import re
    numbers = re.findall(r'\d+[,\d]*\s*\w+', obj) if obj else []
    
    # Query 1: Subject + key number/fact
    if subject and numbers:
        queries.append(f"{subject} {numbers[0]}")
    elif subject and obj:
        # Take first 3 words of object
        obj_short = ' '.join(obj.split()[:3])
        queries.append(f"{subject} {obj_short}")
    
    # Query 2: Subject + location (avoid duplicates)
    if subject and location and location.lower() not in subject.lower():
        queries.append(f"{subject} {location}")
    
    # Query 3: Subject + predicate (simplified)
    if subject and predicate:
        # Simplify predicate (e.g., "be visible" -> "visible")
        pred_simple = predicate.replace('be ', '').replace('is ', '').strip()
        if pred_simple and len(pred_simple) > 2:
            queries.append(f"{subject} {pred_simple}")
    
    # Query 4: Just subject (fallback)
    if subject and not queries:
        queries.append(subject)
    
    # Add context if provided
    if context:
        queries = [f"{context} {q}" for q in queries]
    
    # Clean up: remove duplicates, empty, and too-long queries
    seen = set()
    final_queries = []
    for q in queries:
        q_clean = q.strip()
        q_lower = q_clean.lower()
        word_count = len(q_clean.split())
        
        if (q_clean and 
            q_lower not in seen and 
            word_count >= 2 and 
            word_count <= 6):  # 2-6 words ideal
            seen.add(q_lower)
            final_queries.append(q_clean)
    
    return final_queries[:3]  # Max 3 queries