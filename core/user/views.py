from django.shortcuts import render
from django.shortcuts import render
def home(request):
    return render(request, 'user/home.html')

def scan_demo(request):
    return render(request, 'user/scan.html')

def login_view(request):
    return render(request, 'user/login.html')

def register_view(request):
    return render(request, 'user/register.html')

def dashboard_view(request):
    return render(request, 'user/dashboard.html')

def coa_view(request):
    return render(request, 'user/form1.html')
