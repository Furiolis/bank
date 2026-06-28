from django.urls import path
from . import views
app_name="transfers"
urlpatterns = [
    path("", views.transfers, name="transfers"),
    path("internal/", views.internal_transfer, name="internal"),
    path("external/", views.external_transfer, name="external"),   
]
