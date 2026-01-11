# notes/services/veo3_generator.py
"""
Veo 3 Video Generation Service
Generates professional news broadcast videos from extracted claims
"""

import os
import time
import google.generativeai as genai
from django.core.files.base import ContentFile
from django.conf import settings
from ..models import NewsReport, VideoGenerationJob, Claim


def configure_gemini():
    """Configure Gemini API with proper error handling"""
    api_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        raise ValueError(
            "❌ GEMINI_API_KEY not configured. "
            "Please add GEMINI_API_KEY to your environment variables or settings.py"
        )
    
    print(f"✅ Configuring Gemini API...")
    genai.configure(api_key=api_key)
    print(f"✅ Gemini API configured successfully")


def build_video_script(report):
    """Build video script from claims"""
    claims = report.claims.all()
    
    language_names = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'hi': 'Hindi',
        'zh': 'Chinese',
        'ar': 'Arabic',
    }
    
    language = language_names.get(report.language, 'English')
    
    script_parts = [
        f"News Report: {report.title}",
        f"Language: {language}",
        "",
        "Key Claims:",
    ]
    
    for i, claim in enumerate(claims, 1):
        script_parts.append(f"{i}. {claim.title}")
        script_parts.append(f"   Status: {claim.get_status_display()}")
        if claim.verification_notes:
            script_parts.append(f"   Notes: {claim.verification_notes[:200]}")
        script_parts.append("")
    
    return "\n".join(script_parts)


def generate_veo3_prompt(report):
    """Generate optimized prompt for Veo 3"""
    claims = report.claims.all()
    
    # Build structured prompt for news video
    prompt_parts = [
        "Create a professional news broadcast video with the following elements:",
        "",
        f"Title: {report.title}",
        "",
        "Visual Style:",
        "- Clean, modern news studio aesthetic",
        "- Professional lighting and composition",
        "- News ticker at the bottom showing headlines",
        "- Subtle background graphics",
        "",
        "Content Structure:",
    ]
    
    for i, claim in enumerate(claims[:5], 1):  # Limit to 5 claims for video
        status_color = {
            'verified': 'green checkmark',
            'false': 'red X',
            'misleading': 'yellow warning',
            'pending': 'blue question mark'
        }.get(claim.status, 'neutral icon')
        
        prompt_parts.append(f"{i}. Show claim: \"{claim.title[:100]}\"")
        prompt_parts.append(f"   Display {status_color} indicator")
        prompt_parts.append(f"   Show brief supporting visuals")
        prompt_parts.append("")
    
    prompt_parts.extend([
        "Technical Requirements:",
        "- Duration: 30-60 seconds",
        "- High quality 1080p",
        "- Smooth transitions between claims",
        "- Professional news broadcast style",
        "- Clear, readable text overlays",
        "",
        f"Language: {report.get_language_display()}",
    ])
    
    return "\n".join(prompt_parts)


def generate_video_with_veo3(report_id, job_id):
    """
    Generate video using Google Veo 3 via Gemini API
    This is a placeholder implementation as Veo 3 video generation
    API may have specific requirements
    """
    try:
        report = NewsReport.objects.get(id=report_id)
        job = VideoGenerationJob.objects.get(id=job_id)
        
        job.status = 'processing'
        job.save()
        print(f"🎬 Starting video generation for report: {report.title}")
        
        # Configure Gemini
        configure_gemini()
        
        # Build script and prompt
        script = build_video_script(report)
        veo3_prompt = generate_veo3_prompt(report)
        
        # Save prompt to report
        report.video_prompt = veo3_prompt
        report.save()
        
        print(f"📝 Generated video script ({len(script)} chars)")
        
        # Use Gemini to generate enhanced video production plan
        # Try gemini-2.0-flash first (newest), fallback to gemini-1.5-pro
        # Use Veo for video generation
        try:
    # Veo uses a different API endpoint - typically through Vertex AI or specific video generation endpoint
            model = genai.GenerativeModel('veo-2.0')  # or 'veo-001' depending on availability
            
            # For video generation, you'll likely need to use a different method
            response = model.generate_video(
                prompt="Your video description here",
                # Additional parameters like duration, aspect_ratio, etc.
            )
            print("✅ Using Veo 2.0 model for video generation")
        except Exception as e:
            print(f"❌ Veo model not available: {e}")
        
        enhanced_prompt = f"""You are a professional video production assistant for news broadcasts.
Generate a HIGHLY DETAILED video production plan based on this prompt:

{veo3_prompt}

IMPORTANT: This will be used to create an actual video, so be VERY specific.

Provide EXACTLY this structure:

## VIDEO STRUCTURE
- Opening: [30 seconds - describe visuals]
- Content: [describe layout for claims display]
- Closing: [describe closing scene]

## VISUAL ELEMENTS
1. Background: [detailed description]
2. Graphics: [what graphics to show]
3. Text Overlays: [what text, where, colors]

## TIMING
- Total Duration: 60 seconds
- Opening: 0-5s
- Claims: 5-55s (10s each)
- Closing: 55-60s

## CLAIMS TO DISPLAY
"""
        
        # Add claims to prompt
        for i, claim in enumerate(report.claims.all()[:5], 1):
            status_emoji = {'verified': '✅', 'false': '❌', 'misleading': '⚠️', 'pending': '❓'}.get(claim.status, '❓')
            enhanced_prompt += f"\n{i}. {status_emoji} {claim.title[:80]}"
            if claim.verification_notes:
                enhanced_prompt += f"\n   Notes: {claim.verification_notes[:100]}"
        
        enhanced_prompt += "\n\nMake it professional, engaging, and suitable for news broadcast."
        
        response = model.generate_content(enhanced_prompt)
        print(f"✅ Generated production plan ({len(response.text)} chars)")
        
        # Store the production plan along with original script
        full_content = f"""=== NEWS BROADCAST SCRIPT ===
{script}

=== VIDEO PRODUCTION PLAN ===
{response.text}

=== GENERATION INFO ===
Report: {report.title}
Format: Video (Veo 3)
Language: {report.get_language_display()}
Claims: {report.claims.count()}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        report.content = full_content
        report.save()
        
        # Mark job as completed
        job.status = 'completed'
        job.save()
        
        print(f"✅ Video generation completed for report {report.id}")
        
        return {
            'success': True,
            'job_id': job.id,
            'report_id': report.id,
            'message': 'Video production plan generated successfully',
            'content': full_content
        }
        
    except Exception as e:
        print(f"❌ Video generation error: {str(e)}")
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        raise


def check_veo3_job_status(veo3_job_id):
    """
    Check status of Veo 3 video generation job
    Placeholder for actual API implementation
    """
    # TODO: Implement when Veo 3 API is available
    pass


def download_veo3_video(veo3_job_id, report):
    """
    Download generated video from Veo 3
    Placeholder for actual API implementation
    """
    # TODO: Implement when Veo 3 API is available
    pass