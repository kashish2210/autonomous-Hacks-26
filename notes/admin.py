# notes/admin.py
from django.contrib import admin
from .models import Claim, NewsReport, VideoGenerationJob


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['title_preview', 'status', 'language', 'source_type', 'created_at', 'created_by']
    list_filter = ['status', 'language', 'source_type', 'created_at', 'is_archived']
    search_fields = ['title', 'content', 'tags', 'source_url']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'status')
        }),
        ('Source Details', {
            'fields': ('source_url', 'source_type')
        }),
        ('Verification', {
            'fields': ('verification_notes',)
        }),
        ('Classification', {
            'fields': ('language', 'tags')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at', 'is_archived'),
            'classes': ('collapse',)
        }),
    )
    
    def title_preview(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_preview.short_description = 'Title'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('created_by')


@admin.register(NewsReport)
class NewsReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'format_type', 'language', 'claims_count', 'generated_at', 'created_by']
    list_filter = ['format_type', 'language', 'generated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['generated_at']
    filter_horizontal = ['claims']
    
    fieldsets = (
        ('Report Details', {
            'fields': ('title', 'format_type', 'language')
        }),
        ('Content', {
            'fields': ('content', 'claims')
        }),
        ('PDF Output', {
            'fields': ('pdf_file',),
            'classes': ('collapse',)
        }),
        ('Video Output', {
            'fields': ('video_file', 'video_prompt'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'generated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def claims_count(self, obj):
        return obj.claims.count()
    claims_count.short_description = 'Claims'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('created_by').prefetch_related('claims')


@admin.register(VideoGenerationJob)
class VideoGenerationJobAdmin(admin.ModelAdmin):
    list_display = ['id', 'report_title', 'status', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at', 'completed_at']
    search_fields = ['report__title', 'veo3_job_id']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('report', 'status', 'veo3_job_id')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def report_title(self, obj):
        return obj.report.title
    report_title.short_description = 'Report'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('report')