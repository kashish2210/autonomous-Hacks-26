from django.urls import path
from . import views


urlpatterns = [
    path('extract-claims/', views.extract_claims, name='extract_claims'),
]