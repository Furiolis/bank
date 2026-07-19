from django.urls import path
from . import views
app_name="transfers"
urlpatterns = [
    path("transfer/", views.transfer, name="transfer"),
    path("history/", views.history, name="history")
]
