# notes/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Claim(models.Model):
    """Model to store claims extracted from various sources"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('false', 'False'),
        ('misleading', 'Misleading'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('hi', 'Hindi'),
        ('zh', 'Chinese'),
        ('ar', 'Arabic'),
    ]
    
    title = models.CharField(max_length=500)
    content = models.TextField()
    source_url = models.URLField(blank=True, null=True)
    source_type = models.CharField(max_length=50, default='text')  # text, youtube, article
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_notes = models.TextField(blank=True)
    
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    is_archived = models.BooleanField(default=False)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title[:50]}... ({self.status})"
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []


class NewsReport(models.Model):
    """Model to store generated news reports"""
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF Document'),
        ('video', 'Video (Veo 3)'),
    ]
    
    title = models.CharField(max_length=500)
    claims = models.ManyToManyField(Claim, related_name='reports')
    
    format_type = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    language = models.CharField(max_length=5, choices=Claim.LANGUAGE_CHOICES, default='en')
    
    content = models.TextField(help_text="Generated report content/script")
    
    pdf_file = models.FileField(upload_to='reports/pdf/', blank=True, null=True)
    video_file = models.FileField(upload_to='reports/video/', blank=True, null=True)
    video_prompt = models.TextField(blank=True, help_text="Prompt sent to Veo 3")
    
    generated_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} ({self.format_type})"


class VideoGenerationJob(models.Model):
    """Track video generation jobs"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    report = models.ForeignKey(NewsReport, on_delete=models.CASCADE, related_name='video_jobs')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    veo3_job_id = models.CharField(max_length=200, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Video Job {self.id} - {self.status}"