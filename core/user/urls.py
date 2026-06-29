from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('scan/', views.scan_demo, name='scan_demo'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/approve/<int:doc_id>/', views.approve_document, name='approve_document'),
    path('dashboard/reject/<int:doc_id>/', views.reject_document, name='reject_document'),
    path('profile/', views.profile_view, name='profile'),
    path('coa/', views.coa_view, name='coa_report'),
]
