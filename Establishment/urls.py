from django.urls import path
from .views import PublicAgenda, SaveInfosView, SaveAddressView, SaveOperatingHoursView

app_name = "establishment"

urlpatterns = [
    path("e/<str:uid>/", PublicAgenda.as_view(), name="public_agenda"),
    path("infos/save/", SaveInfosView.as_view(), name="save_infos"),
    path("address/save/", SaveAddressView.as_view(), name="save_address"),
    path("operating-hours/save/", SaveOperatingHoursView.as_view(), name="save_operating_hours"),
]
