from django.db import models
from django.utils import timezone

class Article(models.Model):
    """Model for storing analyzed articles"""
    
    title = models.CharField(max_length=500)
    content = models.TextField()
    url = models.URLField(max_length=1000, blank=True, null=True)
    
    # Source data
    named_sources = models.JSONField(default=list)
    anonymous_phrases = models.JSONField(default=list)
    unique_source_count = models.IntegerField(default=0)
    
    # Scores and analysis
    transparency_score = models.FloatField(default=0.0)
    red_flags = models.JSONField(default=list)
    source_breakdown = models.JSONField(default=dict)
    attribution_patterns = models.JSONField(default=dict)
    
    # Metadata
    analyzed_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-analyzed_at']
        verbose_name = 'Article Analysis'
        verbose_name_plural = 'Article Analyses'
    
    def __str__(self):
        return f"{self.title[:50]} - Score: {self.transparency_score}"
    
    @property
    def bias_analysis(self):
        """Helper property to access bias analysis from attribution_patterns"""
        return self.attribution_patterns.get('bias_analysis', [])
    
    @property
    def source_quality(self):
        """Helper property to access source quality from attribution_patterns"""
        return self.attribution_patterns.get('source_quality', {})
    
    @property
    def recommendations(self):
        """Helper property to access recommendations from attribution_patterns"""
        return self.attribution_patterns.get('recommendations', [])