from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/logs/detail/<int:log_id>/', views.log_detail_api, name='log_detail_api'),
]
