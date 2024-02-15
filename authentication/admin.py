from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from .models import ASquareUser, TempASquareUser


# User creation form for casper user
class ASquareUserCreationForm(forms.ModelForm):
    # A form for creating new users. Includes all the required
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    c_password = forms.CharField(label='Confirmation Password', widget=forms.PasswordInput)

    class Meta:
        model = ASquareUser
        fields = ('first_name', 'last_name', 'username', 'email', 'phone')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("c_password")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# User admin class for asquare user
class ASquareUserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # form = UserChangeForm
    add_form = ASquareUserCreationForm

    # The fields to be used in displaying the User model.
    list_display = (
        'id', 'name', 'username', 'email', 'phone', 'is_super_admin', 'is_store_admin', 'is_staff',
        'is_active')
    list_filter = ('is_store_admin', 'is_super_admin')

    # These are the fields that are visible while editing a user.
    fieldsets = (
        ('Login Credentials', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (('first_name', 'last_name',), 'username', 'phone',)}),
        ('Permissions', {'fields': ('is_super_admin', 'is_store_admin', 'is_staff', 'is_active',)}),
    )

    # These are the fields that will be visible while creating a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'email', 'phone', 'password', 'c_password', 'is_staff', 'is_store_admin',
                'is_active')
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


# TempUser Admin
class TempASquareUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'phone', 'otp', 'is_verified', 'created_at', 'updated_at')
    list_filter = ('is_verified',)
    search_fields = ('email',)
    ordering = ('-created_at',)


# Now register the new CasperUserAdmin...
admin.site.register(ASquareUser, ASquareUserAdmin)
admin.site.unregister(Group)
admin.site.register(TempASquareUser, TempASquareUserAdmin)
