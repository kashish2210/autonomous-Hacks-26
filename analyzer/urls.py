from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='analyzer'),
    path('analyze/', views.analyze_article_stream, name='analyze'),
    path('analyze-stream/', views.analyze_article_stream, name='analyze_stream'),
    path('results/<int:article_id>/', views.results, name='results'),
]