from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('establishment/', include('establishment.urls')),
    path('client-portal/', include('client_portal.urls')),
    path('admin-portal/', include('admin_portal.urls')),
    path('appointment/', include('appointment.urls')),
    path('services/', include('services.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )
