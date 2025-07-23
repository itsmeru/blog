from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_active')
    search_fields = ('username', 'email') 