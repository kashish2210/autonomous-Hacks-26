# ✅ Veo 3 Feature Configuration Checklist

## Pre-Launch Verification

### 📋 Configuration
- [ ] Gemini API key added to `.env` or `settings.py`
  ```
  GEMINI_API_KEY=your_key_here
  ```
- [ ] Media directory exists: `media/reports/pdf/`, `media/reports/video/`
- [ ] Django DEBUG = True (for development)
- [ ] CSRF token configured
- [ ] Static files collected (if needed)

### 🗄️ Database
- [ ] Migrations applied: `python manage.py migrate`
- [ ] VideoGenerationJob model exists
- [ ] NewsReport model exists
- [ ] Claim model exists

### 🌐 URLs
- [ ] `/notes/` - Notes list page ✅
- [ ] `/notes/generate-report/` - Report generation endpoint ✅
- [ ] `/notes/video-status/<job_id>/` - Status check endpoint ✅
- [ ] `/notes/download-report/<report_id>/` - Download endpoint ✅
- [ ] `/media/` - Media files serving ✅

### 📄 Templates
- [ ] `notes/templates/notes/generate_report.html` - Report generation form ✅
- [ ] `notes/templates/notes/notes_list.html` - Claims list ✅

### 🔧 Backend
- [ ] `notes/views.py` - All views implemented ✅
- [ ] `notes/services/veo3_generator.py` - Video generation service ✅
- [ ] `notes/models.py` - Database models defined ✅

## Feature Validation

### Step 1: Extract Claims
```
1. Go to http://127.0.0.1:8000/agent/extract-claims/
2. Enter: "The Earth's atmosphere is 78% nitrogen and 21% oxygen"
3. Wait for verification
4. Check claims appear in http://127.0.0.1:8000/notes/
```
Expected: ✅ Claims appear in notes with verification status

### Step 2: Generate Video Report
```
1. Go to http://127.0.0.1:8000/notes/
2. Check 2-3 claims
3. Click "Generate Report"
4. Select "Video" format
5. Enter title: "Test Video Report"
6. Select language: English
7. Click "Generate"
```
Expected: ✅ Status updates show "processing" → "completed"

### Step 3: Download Production Plan
```
1. When status shows ✅ completed
2. Click "Download Production Plan"
3. Verify .txt file downloads
4. Check file contains:
   - Broadcast script
   - Video production plan
   - Timing specifications
```
Expected: ✅ Text file downloads with full production plan

## Error Handling

### Common Issues & Solutions

**Issue 1: "GEMINI_API_KEY not found"**
```
Solution:
- Add to .env: GEMINI_API_KEY=your_key
- Or add to settings.py: GEMINI_API_KEY = 'your_key'
- Restart Django server
```

**Issue 2: "No claims found"**
```
Solution:
- Go to /agent/extract-claims/
- Extract some claims first
- Wait for verification
- Refresh /notes/ page
```

**Issue 3: "Video generation failed"**
```
Solution:
- Check Gemini API key is valid
- Verify internet connection
- Check Django logs for error details
- Try with fewer claims (max 5)
```

**Issue 4: "Can't download file"**
```
Solution:
- Wait for status to show ✅ (green)
- Check /media/ URL is configured
- Verify media directory exists
- Check browser download settings
```

## Performance Notes

- Video generation time: 30-60 seconds
- Typical file size: 5-10KB (text production plan)
- API calls per report: 2-3 (Gemini API)
- Database queries: ~5-7 per generation

## Security Checklist

- [ ] Gemini API key stored safely (not in git)
- [ ] CSRF token protection enabled
- [ ] User authentication configured
- [ ] File upload/download validation
- [ ] SQL injection prevention (Django ORM)
- [ ] XSS protection enabled

## Monitoring

### Logs to Check
```bash
# Django development server logs show:
- "🎬 Starting video generation..."
- "📝 Generated video script..."
- "✅ Generated production plan..."
- "✅ Video generation completed..."
```

### Database Tables to Monitor
```sql
SELECT * FROM notes_videogenerationjob;
SELECT * FROM notes_newsreport;
SELECT * FROM notes_claim;
```

## Deployment Readiness

For production deployment:
- [ ] Set DEBUG = False
- [ ] Configure proper STATIC_ROOT
- [ ] Configure proper MEDIA_ROOT
- [ ] Use production-grade server (Gunicorn, uWSGI)
- [ ] Set up Nginx for static/media serving
- [ ] Use environment variables for API keys
- [ ] Set up HTTPS/SSL
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Set up database backups
- [ ] Monitor error logs with Sentry or similar

## Testing Commands

```bash
# Test Gemini API connection
python manage.py shell
>>> from notes.services.veo3_generator import configure_gemini
>>> configure_gemini()
>>> print("✅ API configured successfully")

# Check database models
python manage.py shell
>>> from notes.models import Claim, NewsReport, VideoGenerationJob
>>> print(f"Claims: {Claim.objects.count()}")
>>> print(f"Reports: {NewsReport.objects.count()}")
>>> print(f"Jobs: {VideoGenerationJob.objects.count()}")

# Test video generation
python manage.py shell
>>> from notes.models import Claim, NewsReport, VideoGenerationJob
>>> from notes.services.veo3_generator import generate_video_with_veo3
>>> # Create test data first, then call generate_video_with_veo3(report_id, job_id)
```

## Support & Documentation

- 📖 Full User Guide: `VEO3_FEATURE_GUIDE.md`
- 🚀 Quick Start: `QUICK_START_VIDEO.md`
- 📋 Implementation Details: `VIDEO_IMPLEMENTATION_SUMMARY.md`
- 📝 This File: Configuration Checklist

---

**Last Updated:** January 11, 2026
**Version:** 1.0
**Status:** Ready for Testing ✅

Once all checkboxes are completed, the feature is ready for production!
