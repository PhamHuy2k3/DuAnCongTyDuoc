from django.shortcuts import render

def home(request):
    return render(request, 'coreapp/home.html')

def scan_demo(request):
    return render(request, 'coreapp/scan.html')

def login_view(request):
    return render(request, 'coreapp/login.html')

def register_view(request):
    return render(request, 'coreapp/register.html')

def dashboard_view(request):
    return render(request, 'coreapp/dashboard.html')

def coa_view(request):
    return render(request, 'coreapp/form1.html')
