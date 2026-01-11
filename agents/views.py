# agents/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import traceback
from .forms import ClaimsExtractorForm
from agents.verifier.pipeline import verifier_run_pipeline

def extract_claims(request):
    submitted_text = None

    if request.method == "POST":
        form = ClaimsExtractorForm(request.POST)
        if form.is_valid():
            submitted_text = form.cleaned_data["content"]
            claims = verifier_run_pipeline(submitted_text)
            
            # AUTO-SAVE CLAIMS TO NOTES DATABASE
            try:
                from notes.models import Claim
                
                saved_count = 0
                for claim_data in claims:
                    try:
                        # Extract claim information
                        # Handle different possible formats
                        if isinstance(claim_data, dict):
                            claim_text = claim_data.get('canonical_claim', claim_data.get('claim', claim_data.get('text', '')))
                            
                            # Get verification info
                            verification = claim_data.get('verification', {})
                            if isinstance(verification, dict):
                                verification_status = verification.get('verdict', 'UNVERIFIABLE')
                                confidence = verification.get('confidence', 0.0)
                                reasoning = verification.get('reasoning', '')
                                sources = verification.get('evidence_sources', [])
                            else:
                                verification_status = claim_data.get('verification', claim_data.get('status', 'UNVERIFIABLE'))
                                confidence = claim_data.get('confidence', 0.0)
                                reasoning = claim_data.get('reasoning', '')
                                sources = claim_data.get('sources', [])
                        elif isinstance(claim_data, str):
                            # If it's just a string, use it as the claim
                            claim_text = claim_data
                            verification_status = 'UNVERIFIABLE'
                            confidence = 0.0
                            reasoning = ''
                            sources = []
                        else:
                            continue
                        
                        # Skip empty claims
                        if not claim_text or claim_text.strip() == '':
                            continue
                        
                        # DEBUG: Temporarily save ALL claims to debug the issue
                        # TODO: Change back to filtering only VERIFIED when working properly
                        # if verification_status not in ['VERIFIED', 'TRUE', 'PARTIALLY_VERIFIED']:
                        #     print(f"   ⏭️  Skipping (not verified): {claim_text[:60]}... ({verification_status})")
                        #     continue
                        
                        # Map verification status to our status choices
                        status_mapping = {
                            'VERIFIED': 'verified',
                            'TRUE': 'verified',
                            'PARTIALLY_VERIFIED': 'verified',
                            'FALSE': 'false',
                            'MISLEADING': 'misleading',
                            'UNVERIFIABLE': 'pending',
                            'PENDING': 'pending',
                        }
                        
                        db_status = status_mapping.get(
                            verification_status.upper() if isinstance(verification_status, str) else 'PENDING',
                            'pending'
                        )
                        
                        # Build verification notes
                        verification_notes_parts = []
                        if reasoning:
                            verification_notes_parts.append(f"Reasoning: {reasoning}")
                        if confidence:
                            verification_notes_parts.append(f"Confidence: {confidence:.0%}")
                        if sources:
                            verification_notes_parts.append(f"Sources: {', '.join(sources[:3])}")
                        
                        verification_notes = '\n'.join(verification_notes_parts)
                        
                        # Create title from first 100 chars of claim
                        title = claim_text[:100] + '...' if len(claim_text) > 100 else claim_text
                        
                        # Save to database
                        Claim.objects.create(
                            title=title,
                            content=claim_text,
                            verification_notes=verification_notes,
                            status=db_status,
                            source_type='text',
                            created_by=request.user if request.user.is_authenticated else None
                        )
                        saved_count += 1
                        print(f"   ✅ Saved: {claim_text[:60]}... (confidence: {confidence:.0%})")
                        
                    except Exception as e:
                        print(f"Error saving individual claim: {str(e)}")
                        continue
                
                print(f"[Auto-save] Successfully saved {saved_count} VERIFIED claims to Notes database")
                
            except ImportError:
                print("[Auto-save] Notes app not available - claims not saved")
            except Exception as e:
                print(f"[Auto-save] Error saving claims: {str(e)}")
                traceback.print_exc()

            return render(request, "claim_list.html", {'claims': claims})
    else:
        form = ClaimsExtractorForm()

    return render(request, "extract_claims_form.html", {
        "form": form,
        "submitted_text": submitted_text
    })

@ensure_csrf_cookie
def yt_analyzer(request):
    """Render the YouTube analyzer page"""
    return render(request, 'yt_analyzer.html')

@require_http_methods(["POST"])
def load_transcript_view(request):
    """Load transcript from YouTube URL"""
    try:
        # Parse JSON body
        try:
            data = json.loads(request.body)
            print(f"[View] Received data: {data}")
        except json.JSONDecodeError as e:
            print(f"[View] JSON decode error: {str(e)}")
            print(f"[View] Request body: {request.body}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        
        url = data.get('url')
        
        if not url:
            print("[View] No URL provided in request")
            return JsonResponse({
                'success': False,
                'error': 'No URL provided'
            }, status=400)
        
        print(f"[View] Loading transcript for URL: {url}")
        
        # Import and use the extractor
        try:
            from .yt_transcript_extractor.extractor import load_transcript
            print("[View] Extractor module imported successfully")
            print("[View] Starting transcript extraction...")
            
            transcript_docs = load_transcript(url)
            
            if transcript_docs and len(transcript_docs) > 0:
                transcript_text = transcript_docs[0].page_content
                print(f"[View] Success! Transcript length: {len(transcript_text)} characters")
                print(f"[View] Preview: {transcript_text[:100]}...")
                
                # Extract and save claims from transcript
                try:
                    claims = verifier_run_pipeline(transcript_text)
                    
                    # AUTO-SAVE CLAIMS TO NOTES DATABASE
                    from notes.models import Claim
                    
                    saved_count = 0
                    for claim_data in claims:
                        try:
                            # Extract claim information
                            if isinstance(claim_data, dict):
                                claim_text = claim_data.get('canonical_claim', claim_data.get('claim', claim_data.get('text', '')))
                                
                                # Get verification info
                                verification = claim_data.get('verification', {})
                                if isinstance(verification, dict):
                                    verification_status = verification.get('verdict', 'UNVERIFIABLE')
                                    confidence = verification.get('confidence', 0.0)
                                    reasoning = verification.get('reasoning', '')
                                    sources = verification.get('evidence_sources', [])
                                else:
                                    verification_status = claim_data.get('verification', 'UNVERIFIABLE')
                                    confidence = claim_data.get('confidence', 0.0)
                                    reasoning = claim_data.get('reasoning', '')
                                    sources = claim_data.get('sources', [])
                            elif isinstance(claim_data, str):
                                claim_text = claim_data
                                verification_status = 'UNVERIFIABLE'
                                confidence = 0.0
                                reasoning = ''
                                sources = []
                            else:
                                continue
                            
                            if not claim_text or claim_text.strip() == '':
                                continue
                            
                            # DEBUG: Temporarily save ALL claims
                            # TODO: Change back to filtering when working properly
                            # if verification_status not in ['VERIFIED', 'TRUE', 'PARTIALLY_VERIFIED']:
                            #     print(f"   ⏭️  Skipping (not verified): {claim_text[:60]}... ({verification_status})")
                            #     continue
                            
                            # Map status
                            status_mapping = {
                                'VERIFIED': 'verified',
                                'TRUE': 'verified',
                                'PARTIALLY_VERIFIED': 'verified',
                                'FALSE': 'false',
                                'MISLEADING': 'misleading',
                                'UNVERIFIABLE': 'pending',
                                'PENDING': 'pending',
                            }
                            
                            db_status = status_mapping.get(
                                verification_status.upper() if isinstance(verification_status, str) else 'PENDING',
                                'pending'
                            )
                            
                            # Build verification notes
                            verification_notes_parts = []
                            if reasoning:
                                verification_notes_parts.append(f"Reasoning: {reasoning}")
                            if confidence:
                                verification_notes_parts.append(f"Confidence: {confidence:.0%}")
                            if sources:
                                verification_notes_parts.append(f"Sources: {', '.join(sources[:3])}")
                            
                            verification_notes = '\n'.join(verification_notes_parts)
                            
                            # Create title
                            title = claim_text[:100] + '...' if len(claim_text) > 100 else claim_text
                            
                            # Save to database
                            Claim.objects.create(
                                title=title,
                                content=claim_text,
                                source_url=url,
                                source_type='youtube',
                                verification_notes=verification_notes,
                                status=db_status,
                                created_by=request.user if request.user.is_authenticated else None
                            )
                            saved_count += 1
                            print(f"   ✅ Saved: {claim_text[:60]}... (confidence: {confidence:.0%})")
                            
                        except Exception as e:
                            print(f"[YT Auto-save] Error saving individual claim: {str(e)}")
                            continue
                    
                    print(f"[YT Auto-save] Successfully saved {saved_count} VERIFIED claims from YouTube transcript")
                    
                except Exception as e:
                    print(f"[YT Auto-save] Error in claim extraction/saving: {str(e)}")
                    traceback.print_exc()
                
                return JsonResponse({
                    'success': True,
                    'transcript': transcript_text
                })
            else:
                print("[View] No transcript documents returned")
                return JsonResponse({
                    'success': False,
                    'error': 'No transcript available for this video'
                }, status=404)
                
        except ImportError as e:
            print(f"[View] Import error: {str(e)}")
            print("[View] Full traceback:")
            traceback.print_exc()
            
            # Check if youtube_transcript_api is installed
            try:
                import youtube_transcript_api
                print(f"[View] youtube_transcript_api version: {youtube_transcript_api.__version__}")
            except ImportError:
                print("[View] youtube_transcript_api is NOT installed!")
                return JsonResponse({
                    'success': False,
                    'error': 'YouTube transcript API not installed. Please run: pip install youtube-transcript-api'
                }, status=500)
            
            return JsonResponse({
                'success': False,
                'error': f'Import error: {str(e)}'
            }, status=500)
            
        except Exception as e:
            error_message = str(e)
            print(f"[View] Error during extraction: {error_message}")
            print("[View] Full traceback:")
            traceback.print_exc()
            
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=500)
            
    except Exception as e:
        print(f"[View] Unexpected error: {str(e)}")
        print("[View] Full traceback:")
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)