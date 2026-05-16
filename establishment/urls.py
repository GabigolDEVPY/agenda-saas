from django.urls import path
from . views import SaveAddressView, SaveInfosView, SaveOperatingHoursView, GeneralPreferencesView

app_name = 'establishment'

urlpatterns = [
    path('infos/save/', SaveInfosView.as_view(), name='save_infos'),
    path('address/save/', SaveAddressView.as_view(), name='save_address'),


    # alter operating days and hours
    path('operating/day-alter', SaveOperatingHoursView.as_view(), name='day_alter'),
    path('operating/day-open', SaveInfosView.as_view(), name='day_open'),
    path('operating/day-close', SaveInfosView.as_view(), name='day_close'),

    #general preferences
    path('general-preferences/update', GeneralPreferencesView.as_view(), name="general_preference_update")
]

