from django.shortcuts import render

# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')
def contact(request):
    return render(request, 'contact.html')
def privacy(request):
    return render(request, 'privacy.html')
