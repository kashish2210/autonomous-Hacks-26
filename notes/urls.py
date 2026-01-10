# notes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main notes list
    path('', views.notes_list, name='notes_list'),
    
    # Claim CRUD operations
    path('claim/new/', views.claim_create, name='claim_new'),
    path('claim/<int:claim_id>/edit/', views.claim_edit, name='claim_edit'),
    path('claim/<int:claim_id>/delete/', views.claim_delete, name='claim_delete'),
    
    # Bulk operations
    path('bulk-save-claims/', views.bulk_save_claims, name='bulk_save_claims'),
    
    # Report generation
    path('generate-report/', views.generate_report, name='generate_report'),
    path('video-status/<int:job_id>/', views.check_video_status, name='check_video_status'),
    path('download-report/<int:report_id>/', views.download_report, name='download_report'),
]