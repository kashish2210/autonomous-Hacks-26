# views_with_search.py (Complete implementation with web search)
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import ClaimsExtractorForm
from .claim_extractor.pipeline import run_pipeline
from .claim_extractor.claim_store import GlobalClaimStore
from .claim_extractor.fact_verifier import FactVerifierAgent
from .web_search_helper import perform_multi_search
import json

# Initialize global store and verifier
# In production, consider using Django cache or database storage
global_store = GlobalClaimStore()
verifier_agent = FactVerifierAgent()


def extract_claims(request):
    submitted_text = None
    claims = None
    error_message = None

    if request.method == "POST":
        form = ClaimsExtractorForm(request.POST)
        if form.is_valid():
            submitted_text = form.cleaned_data["content"]
            
            try:
                # Try to extract claims
                result = run_pipeline(submitted_text)
                claims = result.get('claims', [])
                
                # Pass both claims and submitted_text to the results page
                return render(request, "claim_list.html", {
                    'claims': claims,
                    'submitted_text': submitted_text
                })
                
            except Exception as e:
                # Handle any errors from the pipeline
                error_str = str(e)
                
                # Check if it's a parsing error
                if "Invalid json output" in error_str or "OutputParserException" in error_str:
                    error_message = (
                        "⚠️ The AI model couldn't process this text properly. "
                        "This might happen with very complex or ambiguous sentences. "
                        "Try simplifying your text or breaking it into smaller paragraphs."
                    )
                else:
                    error_message = f"An error occurred while processing your text: {error_str}"
                
                # Return to form with error message
                return render(request, "extract_claims_form.html", {
                    "form": form,
                    "submitted_text": submitted_text,
                    "error_message": error_message
                })
    else:
        form = ClaimsExtractorForm()

    return render(request, "extract_claims_form.html", {
        "form": form,
        "submitted_text": submitted_text,
        "error_message": error_message
    })


def claim_list(request):
    """Display extracted claims"""
    claims = global_store.all()
    submitted_text = request.session.get('submitted_text', '')
    
    # Get verification summary
    summary = global_store.get_verification_summary()
    
    return render(request, "claim_list.html", {
        'claims': claims,
        'submitted_text': submitted_text,
        'summary': summary
    })


def verify_claim(request, canonical_claim):
    """
    Verify a specific claim using web search
    This view will be called via AJAX
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Get the claim from store
    claim = global_store.get_claim(canonical_claim)
    if not claim:
        return JsonResponse({'error': 'Claim not found'}, status=404)
    
    # Check if already verified
    if claim['verification']['verdict'] is not None:
        return JsonResponse({
            'status': 'already_verified',
            'verification': claim['verification']
        })
    
    try:
        # Step 1: Generate search queries
        search_queries = verifier_agent.get_search_queries(canonical_claim)
        
        # Step 2: Perform actual web searches using Google Custom Search
        all_search_results = perform_multi_search(
            search_queries, 
            results_per_query=3
        )
        
        # If no results found, return unverifiable
        if not all_search_results:
            return JsonResponse({
                'status': 'success',
                'verification': {
                    'verdict': 'UNVERIFIABLE',
                    'confidence': 0.0,
                    'reasoning': 'No search results found to verify this claim.',
                    'evidence_sources': []
                }
            })
        
        # Step 3: Verify claim with search results
        verification_result = verifier_agent.verify_claim(
            canonical_claim, 
            all_search_results
        )
        
        # Step 4: Update store
        global_store.update_verification(
            canonical_claim,
            verification_result.verdict,
            verification_result.confidence,
            verification_result.reasoning,
            verification_result.evidence_sources
        )
        
        return JsonResponse({
            'status': 'success',
            'verification': {
                'verdict': verification_result.verdict,
                'confidence': verification_result.confidence,
                'reasoning': verification_result.reasoning,
                'evidence_sources': verification_result.evidence_sources
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


def verify_all_claims(request):
    """
    Verify all unverified claims in batch
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    unverified = global_store.unverified_claims()
    
    results = {
        'total': len(unverified),
        'verified': 0,
        'failed': 0,
        'errors': []
    }
    
    for claim_data in unverified:
        canonical_claim = claim_data['canonical_claim']
        
        try:
            # Generate search queries
            search_queries = verifier_agent.get_search_queries(canonical_claim)
            
            # Perform web searches
            all_search_results = perform_multi_search(
                search_queries,
                results_per_query=3
            )
            
            # Verify claim
            if all_search_results:
                verification_result = verifier_agent.verify_claim(
                    canonical_claim,
                    all_search_results
                )
                
                # Update store
                global_store.update_verification(
                    canonical_claim,
                    verification_result.verdict,
                    verification_result.confidence,
                    verification_result.reasoning,
                    verification_result.evidence_sources
                )
                
                results['verified'] += 1
            else:
                # No search results
                global_store.update_verification(
                    canonical_claim,
                    'UNVERIFIABLE',
                    0.0,
                    'No search results found',
                    []
                )
                results['verified'] += 1
            
        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'claim': canonical_claim,
                'error': str(e)
            })
    
    return JsonResponse(results)


def get_claim_details(request, canonical_claim):
    """Get detailed information about a specific claim"""
    claim = global_store.get_claim(canonical_claim)
    
    if not claim:
        return JsonResponse({'error': 'Claim not found'}, status=404)
    
    return JsonResponse(claim, safe=False)


def export_claims_json(request):
    """Export all claims as JSON"""
    claims = global_store.all()
    return JsonResponse({'claims': claims}, safe=False)