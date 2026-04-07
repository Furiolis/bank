from django.urls import path
from . import views
urlpatterns = [
    path("", views.front_page, name="front_page"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("new-client", views.new_client, name="new_client"),
    path("confirmation", views.confirmation, name="confirmation"),
    path("new-account", views.new_account, name="new_account"),
    path("new-credit", views.new_credit, name="new_credit"),
    path("accounts", views.accounts, name="accounts"),
    path("accounts-manage", views.accounts_manage, name="accounts_manage"),
    path("cards", views.cards, name="cards"),
    path("cards-manage", views.cards_manage, name="cards_manage")
    ]
