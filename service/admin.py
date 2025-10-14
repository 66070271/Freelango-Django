# admin.py
from django.contrib import admin
from .models import PlatformAccount

@admin.register(PlatformAccount)
class PlatformAccountAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "account_name", "account_number")
