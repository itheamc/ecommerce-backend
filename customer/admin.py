from django.contrib import admin
from .models import *


# Admin for Customer Model
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    list_filter = ('is_active',)
    search_fields = ('user',)
    ordering = ('-created_at',)


# Admin for CustomerAddress Model
class CustomerAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'street', 'city', 'province')
    list_filter = ('is_active',)
    search_fields = ('customer', 'city',)
    ordering = ('-created_at',)


# Registering CustomerAdmin
admin.site.register(Customer, CustomerAdmin)
# Registering CustomerAddressAdmin
admin.site.register(CustomerAddress, CustomerAddressAdmin)
