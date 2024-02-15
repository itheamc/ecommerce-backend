from django.contrib import admin
from .models import *


# Category Model Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'display_name', 'description', 'is_active', 'icon_url', 'level',)
    list_filter = ('name',)
    search_fields = ('name',)


# Register your models here.
admin.site.register(Category, CategoryAdmin)
