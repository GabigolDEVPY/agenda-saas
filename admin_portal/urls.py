from django.urls import path
from . views import ServicesView


app_name = 'admin_portal'

urlpatterns = [
    path('', ServicesView.as_view(), name='home'),
]
