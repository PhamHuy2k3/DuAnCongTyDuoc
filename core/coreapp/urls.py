from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='admin_home'),
    path('login/', views.login_view, name='login'),
    path('user/', views.user, name='user' ),
    path('adminqt/', views.adminqt, name='adminqt'),
    path('total/', views.total, name='total'),
    path('logs/today/', views.log_today_view, name='log_today'),
    path('logs/all/', views.log_all_view, name='log_all'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/logs/<str:date_str>/', views.log_detail_view, name='log_detail')
]
