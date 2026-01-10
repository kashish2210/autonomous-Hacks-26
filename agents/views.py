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