from django.urls import path
from . import views


urlpatterns = [
    path('extract_claims/', views.extract_claims)
]