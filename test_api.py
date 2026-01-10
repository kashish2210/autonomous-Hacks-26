"""
Detailed API Inspector
Shows EXACTLY what's in your youtube-transcript-api module
"""

print("=" * 70)
print("YouTube Transcript API Inspector")
print("=" * 70)

try:
    import youtube_transcript_api
    print(f"\n✓ Module imported: {youtube_transcript_api}")
    print(f"  Module file: {youtube_transcript_api.__file__}")
    
    # Show all attributes
    print("\n" + "=" * 70)
    print("All module attributes:")
    print("=" * 70)
    for attr in dir(youtube_transcript_api):
        if not attr.startswith('_'):
            obj = getattr(youtube_transcript_api, attr)
            print(f"  {attr:30} -> {type(obj).__name__}")
    
    # Try to import the main class
    print("\n" + "=" * 70)
    print("Trying to import YouTubeTranscriptApi:")
    print("=" * 70)
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print(f"✓ YouTubeTranscriptApi imported: {YouTubeTranscriptApi}")
        
        # Show class methods
        print("\nClass methods:")
        for method in dir(YouTubeTranscriptApi):
            if not method.startswith('_'):
                print(f"  - {method}")
        
        # Check if it's a class or instance
        print(f"\nType: {type(YouTubeTranscriptApi)}")
        
        # Try to see if we need to instantiate it
        print("\nTrying to create instance...")
        try:
            api_instance = YouTubeTranscriptApi()
            print(f"✓ Instance created: {api_instance}")
            print("\nInstance methods:")
            for method in dir(api_instance):
                if not method.startswith('_'):
                    print(f"  - {method}")
        except Exception as e:
            print(f"Cannot instantiate (might be static): {e}")
        
    except ImportError as e:
        print(f"✗ Cannot import YouTubeTranscriptApi: {e}")
    
    # Try alternative imports
    print("\n" + "=" * 70)
    print("Checking for alternative classes:")
    print("=" * 70)
    
    alternatives = [
        'YouTubeTranscriptApi',
        'Transcript',
        'TranscriptList',
        'YouTubeTranscriptRetriever',
        'get_transcript',
        'list_transcripts',
    ]
    
    for name in alternatives:
        if hasattr(youtube_transcript_api, name):
            obj = getattr(youtube_transcript_api, name)
            print(f"✓ Found: {name} -> {type(obj).__name__}")
        else:
            print(f"✗ Not found: {name}")
    
    # Show package info
    print("\n" + "=" * 70)
    print("Package information:")
    print("=" * 70)
    
    info_attrs = ['__version__', '__author__', '__name__', '__package__']
    for attr in info_attrs:
        if hasattr(youtube_transcript_api, attr):
            print(f"  {attr}: {getattr(youtube_transcript_api, attr)}")
        else:
            print(f"  {attr}: Not available")
    
    # Try a real test
    print("\n" + "=" * 70)
    print("Attempting real transcript fetch:")
    print("=" * 70)
    
    video_id = "jNQXAC9IVRw"
    print(f"Video ID: {video_id}")
    
    # Try different approaches
    approaches = []
    
    # Approach 1: Static method
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        result = YouTubeTranscriptApi.list(video_id)
        approaches.append(("YouTubeTranscriptApi.list(video_id)", "SUCCESS", result))
    except Exception as e:
        approaches.append(("YouTubeTranscriptApi.list(video_id)", "FAILED", str(e)))
    
    # Approach 2: Instance method
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        result = api.list(video_id)
        approaches.append(("api.list(video_id)", "SUCCESS", result))
    except Exception as e:
        approaches.append(("api.list(video_id)", "FAILED", str(e)))
    
    # Approach 3: Get transcript function
    try:
        from youtube_transcript_api import get_transcript
        result = get_transcript(video_id)
        approaches.append(("get_transcript(video_id)", "SUCCESS", result))
    except Exception as e:
        approaches.append(("get_transcript(video_id)", "FAILED", str(e)))
    
    print("\nResults:")
    for approach, status, result in approaches:
        print(f"\n  {approach}")
        print(f"    Status: {status}")
        if status == "SUCCESS":
            print(f"    Result type: {type(result)}")
            print(f"    Result: {str(result)[:100]}")
        else:
            print(f"    Error: {result}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    working_approaches = [a for a in approaches if a[1] == "SUCCESS"]
    if working_approaches:
        print("✓ Working approaches found:")
        for approach, _, _ in working_approaches:
            print(f"  - {approach}")
    else:
        print("✗ No working approaches found!")
        print("\nThis indicates a serious issue with the package.")
        print("Try: pip install youtube-transcript-api==0.6.1")
    
except ImportError as e:
    print(f"\n✗ Cannot import youtube_transcript_api at all!")
    print(f"Error: {e}")
    print("\nInstall it with: pip install youtube-transcript-api")
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)