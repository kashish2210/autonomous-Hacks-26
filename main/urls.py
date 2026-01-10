from django.urls import path
from main.views import contact, dashboard, privacy
urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('contact/', contact, name='contact'),
    path('privacy/', privacy, name='privacy'),
]