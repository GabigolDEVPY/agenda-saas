from django.urls import path

from .views import (
    ServiceCreateView,
    ServiceDeleteView,
    ServiceEditFormView,
    ServiceUpdateView,
)

app_name = "services"

urlpatterns = [
    path("create/", ServiceCreateView.as_view(), name="create_service"),
    path("<int:pk>/edit-form/", ServiceEditFormView.as_view(), name="edit_service_form"),
    path("<int:pk>/update/", ServiceUpdateView.as_view(), name="update_service"),
    path("delete/", ServiceDeleteView.as_view(), name="delete_service"),
]
