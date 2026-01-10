# urls.py - Updated with verification endpoints
from django.urls import path
from . import views

urlpatterns = [
    path('extract_claims/', views.extract_claims, name='extract_claims'),
    path('claims/', views.claim_list, name='claim_list'),
    path('verify/<str:canonical_claim>/', views.verify_claim, name='verify_claim'),
    path('verify-all/', views.verify_all_claims, name='verify_all_claims'),
    path('claim-details/<str:canonical_claim>/', views.get_claim_details, name='claim_details'),
]