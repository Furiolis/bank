from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("review/", views.review, name="review"),
    path("login", views.login, name="login"),
    path("new-client/", views.new, name="new_client"),
    path("confirm", views.confirm, name="confirm"),
]