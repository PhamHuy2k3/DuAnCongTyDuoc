from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from coreapp import views as core_views
from user import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('login/', core_views.login_view, name='login'),
    path('logout/', core_views.logout_view, name='logout'),
    path('', include('coreapp.urls')),
    path('user/', include('user.urls')),
    path('coa/', user_views.coa_view, name='coa_report'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

