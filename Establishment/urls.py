from django.urls import path
from . views import PublicAgenda

app_name = 'establishment'

urlpatterns = [
    path('e/<str:uid>/', PublicAgenda.as_view(), name='public_agenda'),
    # path('e/<str:uid>/servicos/', views.services, name='services'),
    # path('e/<str:uid>/sobre/', views.about, name='about'),
]
