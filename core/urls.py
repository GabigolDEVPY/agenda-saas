from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('servicos/', include('servicos.urls')),
    path('establishment/', include('establishment.urls')),
]