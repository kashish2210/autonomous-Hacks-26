# agents/yt_transcript_extractor/extractor.py
"""
YouTube Transcript Extractor
FINAL WORKING VERSION - Uses instance methods
"""

import re


def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
        r'^([0-9A-Za-z_-]{11})$'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def load_transcript(url):
    """
    Load transcript from YouTube video
    
    Args:
        url (str): YouTube video URL or video ID
        
    Returns:
        list: List containing a single Document-like object with transcript text
    """
    print(f"[Extractor] Starting transcript load for URL: {url}")
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print("[Extractor] ✓ YouTubeTranscriptApi imported")
    except ImportError:
        error_msg = "youtube-transcript-api not installed. Run: pip install youtube-transcript-api"
        print(f"[Extractor] ✗ {error_msg}")
        raise Exception(error_msg)
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        error_msg = "Could not extract video ID from URL"
        print(f"[Extractor] ✗ {error_msg}")
        raise ValueError(error_msg)
    
    print(f"[Extractor] Video ID: {video_id}")
    
    try:
        # CRITICAL: Create an instance first!
        # The API uses INSTANCE methods, not static methods
        print("[Extractor] Creating YouTubeTranscriptApi instance...")
        ytt_api = YouTubeTranscriptApi()
        print("[Extractor] ✓ Instance created")
        
        # Now call list() on the instance
        print("[Extractor] Calling api.list()...")
        transcript_list = ytt_api.list(video_id)
        
        print(f"[Extractor] ✓ Got TranscriptList: {type(transcript_list)}")
        
        # Iterate through available transcripts
        selected_transcript = None
        available_langs = []
        
        print("[Extractor] Available transcripts:")
        for transcript in transcript_list:
            try:
                lang_code = transcript.language_code
                lang_name = transcript.language
                is_generated = transcript.is_generated
                
                available_langs.append(f"{lang_name} ({lang_code})")
                print(f"[Extractor]   - {lang_name} ({lang_code}) {'[auto]' if is_generated else '[manual]'}")
                
                # Select English transcript if available
                if selected_transcript is None:
                    if 'en' in lang_code.lower() or 'english' in lang_name.lower():
                        selected_transcript = transcript
                        print(f"[Extractor] ✓ Selected English transcript")
                
            except Exception as e:
                print(f"[Extractor] Warning: Error reading transcript: {e}")
                continue
        
        # If no English, use first available
        if selected_transcript is None and available_langs:
            print("[Extractor] No English found, using first available...")
            for transcript in transcript_list:
                selected_transcript = transcript
                break
        
        if selected_transcript is None:
            error_msg = f"No transcripts available. Found: {', '.join(available_langs) if available_langs else 'None'}"
            print(f"[Extractor] ✗ {error_msg}")
            raise Exception(error_msg)
        
        # Fetch the transcript data
        print("[Extractor] Fetching transcript data...")
        fetched_transcript = selected_transcript.fetch()
        
        print(f"[Extractor] ✓ Got FetchedTranscript: {type(fetched_transcript)}")
        
        # Convert to raw data (list of dicts)
        print("[Extractor] Converting to raw data...")
        transcript_data = fetched_transcript.to_raw_data()
        
        if not transcript_data:
            error_msg = "Transcript data is empty"
            print(f"[Extractor] ✗ {error_msg}")
            raise Exception(error_msg)
        
        print(f"[Extractor] ✓ Got {len(transcript_data)} segments")
        
        # Combine text
        full_text = " ".join([entry['text'] for entry in transcript_data])
        
        print(f"[Extractor] ✓ Combined text: {len(full_text)} characters")
        print(f"[Extractor] Preview: {full_text[:150]}...")
        
        # Create Document-like object
        class SimpleDocument:
            def __init__(self, content):
                self.page_content = content
        
        print(f"[Extractor] ✓ SUCCESS! Transcript loaded")
        return [SimpleDocument(full_text)]
        
    except ValueError as e:
        raise Exception(str(e))
        
    except Exception as e:
        error_str = str(e).lower()
        
        if 'disabled' in error_str or 'not available' in error_str:
            error_msg = "Transcripts are disabled for this video"
        elif 'unavailable' in error_str or 'private' in error_str:
            error_msg = "Video is unavailable or private"
        elif '429' in error_str or 'rate' in error_str:
            error_msg = "Rate limited. Please wait a few minutes."
        else:
            error_msg = f"Failed to load transcript: {str(e)}"
        
        print(f"[Extractor] ✗ Error: {error_msg}")
        
        import traceback
        print("[Extractor] Full traceback:")
        traceback.print_exc()
        
        raise Exception(error_msg)


if __name__ == '__main__':
    """Test the extractor"""
    import sys
    
    print("=" * 70)
    print("YouTube Transcript Extractor - Self Test")
    print("=" * 70)
    
    # Test API
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print("\n✓ API imported")
        
        # Create instance
        ytt_api = YouTubeTranscriptApi()
        print("✓ Instance created")
        print(f"  Methods: {[m for m in dir(ytt_api) if not m.startswith('_')]}")
    except Exception as e:
        print(f"\n✗ API test failed: {e}")
        sys.exit(1)
    
    # Test videos
    test_videos = [
        ("https://www.youtube.com/watch?v=jNQXAC9IVRw", "TED Talk"),
        ("https://youtu.be/Ks47iOpKOIE", "Your Video"),
    ]
    
    success = 0
    
    for url, desc in test_videos:
        print(f"\n{'='*70}")
        print(f"TEST: {desc}")
        print(f"URL: {url}")
        print('='*70)
        
        try:
            result = load_transcript(url)
            text = result[0].page_content
            
            print(f"\n✓✓✓ SUCCESS ✓✓✓")
            print(f"Characters: {len(text)}")
            print(f"Preview: {text[:200]}...")
            success += 1
            
        except Exception as e:
            print(f"\n✗✗✗ FAILED ✗✗✗")
            print(f"Error: {e}")
    
    print(f"\n{'='*70}")
    print(f"RESULTS: {success}/{len(test_videos)} passed")
    print('='*70)
    
    if success > 0:
        print("\n✓ Extractor is working!")
    else:
        print("\n✗ All tests failed")
    
    sys.exit(0 if success > 0 else 1)