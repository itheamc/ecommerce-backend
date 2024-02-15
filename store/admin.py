from django.contrib import admin
from .models import Store, StoreAddress, StoreStaff, StoreStaffPosition


# StoreModel Admin
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'phone', 'email', 'category', 'type', 'address', 'pan_number', 'is_active',
        'is_approved',)
    list_filter = ('name', 'type',)
    search_fields = ('name', 'phone', 'email', 'pan_number',)


# StoreStaffModel Admin
class StoreStaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'user', 'position',)
    list_filter = ('store',)
    search_fields = ('store', 'user',)


# StoreStaffPositionModel Admin
class StoreStaffPositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_filter = ('name',)
    search_fields = ('name',)


# StoreAddressModel Admin
class StoreAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'street', 'city', 'ward_number', 'municipality', 'district', 'province', 'postal_code',)
    list_filter = ('street', 'city', 'district', 'province', 'postal_code',)
    search_fields = ('street', 'city', 'district', 'province', 'postal_code',)


# Registering the models
admin.site.register(Store, StoreAdmin)
admin.site.register(StoreStaff, StoreStaffAdmin)
admin.site.register(StoreStaffPosition, StoreStaffPositionAdmin)
admin.site.register(StoreAddress, StoreAddressAdmin)
