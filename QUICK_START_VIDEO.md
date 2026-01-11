# 🚀 Quick Start - Veo 3 Video Generation

## 5-Minute Setup

### 1️⃣ Add Gemini API Key
Add to your `.env` file or `credible/settings.py`:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 2️⃣ Restart Django Server
```bash
python manage.py runserver
```

### 3️⃣ Extract Claims
- Go to: `http://127.0.0.1:8000/agent/extract-claims/`
- Enter text with facts to verify
- Wait for processing
- Claims will be automatically verified

### 4️⃣ Generate Video
- Go to: `http://127.0.0.1:8000/notes/`
- Check the claims you want in your video
- Click "Generate Report"
- Choose "Video" format
- Enter report title
- Click "Generate"

### 5️⃣ Download Production Plan
- Wait for completion ✅
- Click "Download Production Plan"
- Save the `.txt` file
- Use it as a blueprint for your video

## What You Get

A professional video production plan including:
- 📝 Complete broadcast script
- 🎥 Shot-by-shot visual breakdown
- ⏱️ Detailed timing specifications
- 🎨 Graphics and animation requirements
- 💬 Text overlay specifications

## Example Output

```
=== NEWS BROADCAST SCRIPT ===
News Report: Today's Top Claims
Language: English

Key Claims:
1. The Earth's atmosphere is 78% nitrogen
   Status: Verified

=== VIDEO PRODUCTION PLAN ===
## VIDEO STRUCTURE
- Opening: Professional news studio with anchor
  Duration: 5 seconds
  Visuals: Clean desk, news ticker at bottom
  
- Content: Claims display with verification status
  Duration: 55 seconds
  Visuals: Split screen with claim text and verification indicator

## TIMING
- Total Duration: 60 seconds
- Opening: 0-5s
- Claim 1: 5-15s
- Claim 2: 15-25s
- Closing: 55-60s
```

## Troubleshooting

**Q: "Video generation failed"**
A: Check your Gemini API key in settings/environment

**Q: "No claims selected"**
A: Go to notes page, check boxes next to claims

**Q: "Can't download file"**
A: Wait for status to show ✅ complete

## Get Help

📖 Full guide: `VEO3_FEATURE_GUIDE.md`
📋 Implementation details: `VIDEO_IMPLEMENTATION_SUMMARY.md`

---

**Ready to create AI videos?** Start now! 🎬
