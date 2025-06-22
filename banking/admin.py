from django.contrib import admin
from .models import Client, Account

# Register your models here.
# class ClientAdmin(admin.ModelAdmin):
#     pass
# class AccountAdmin(admin.ModelAdmin):
#     pass
    
admin.site.register(Client)
admin.site.register(Account)


