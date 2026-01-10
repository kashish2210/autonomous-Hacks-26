from django.urls import path
from . import views


urlpatterns = [
   path('extract-claims/', views.extract_claims, name='extract_claims'),
   path('yt/', views.yt_analyzer, name='yt_analyzer'),
   path('load-transcript/', views.load_transcript_view, name='load_transcript'),
    path('extract-claims/', views.extract_claims, name='extract_claims'),
]