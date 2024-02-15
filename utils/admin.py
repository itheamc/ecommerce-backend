from django.contrib import admin
from .models import *


# Creating ModelAdmin for SupportingInformation
class SupportingInformationAdmin(admin.ModelAdmin):
    list_display = ('title', 'summary', 'updated_at')
    list_filter = ('title',)
    search_fields = ('title', 'summary', 'description_en', 'description_np')
    ordering = ('-created_at',)


# Registering SupportingInformationAdmin
admin.site.register(SupportingInformation, SupportingInformationAdmin)