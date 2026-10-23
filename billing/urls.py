from django.urls import path

from .views import DeleteAccountView


app_name = "billing"

urlpatterns = [
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),
]


