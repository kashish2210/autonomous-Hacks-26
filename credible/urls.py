from django.contrib import admin
from django.urls import path, include
from analyzer import views as analyzer_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('analyzer/', include('analyzer.urls')),
]