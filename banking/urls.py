from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="main_panel"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("new-client", views.new_client, name="new_client"),
    path("confirmation", views.confirmation, name="confirmation"),
    path("new-loan", views.new_loan, name="new_loan"),
    path("new-account", views.new_account, name="new_account"),
    path("new-credit-card", views.new_credit_card, name="new_credit_card")
    ]
