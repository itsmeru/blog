from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone", "nickname", "is_active", "created_at")
    search_fields = ("email", "phone", "nickname")
    list_filter = ("is_active", "created_at")
