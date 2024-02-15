import random
from uuid import uuid4

from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.html import format_html


# -------------------------------@mit--------------------------------
# aSquare User Manager
class ASquareUserManager(BaseUserManager):

    # Create a new user
    def create_user(self, email, password=None, **extra_fields):
        # Checking if email is None or not
        if not email:
            raise ValueError('Email address is required!!')

        # Creates and saves a new user
        extra_fields['username'] = f"{email.split('@')[0]}{random.randint(100, 900)}"
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Create a new superuser
    def create_superuser(self, email, password=None):
        # Creates and saves a new superuser
        user = self.create_user(email, password)
        user.is_super_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


# -------------------------------@mit--------------------------------
# Casper User
class ASquareUser(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid4, editable=False)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True, default="")
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=10, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_store_admin = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # UserManager
    objects = ASquareUserManager()

    # Required for Django
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Required for Permissions
    def has_perm(self, perm, obj=None):
        return self.is_super_admin

    # Required for Permissions
    def has_module_perms(self, app_label):
        return self.is_super_admin

    # Property for full name
    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name) if self.first_name and self.last_name else self.username

    # Property for dictionary
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_staff': self.is_staff,
            'is_store_admin': self.is_store_admin,
            'is_super_admin': self.is_super_admin
        }

    # Property to return the dict
    @property
    def as_dict_min(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'email': self.email,
            'phone': self.phone
        }

    # Formatted full name to display on admin page
    @admin.display
    def name(self):
        return format_html('<span style="color:yellow; font-weight:bold;">{} {}</span>', self.first_name,
                           self.last_name)

    def __str__(self):
        return self.first_name if self.first_name else self.username

    # Meta class
    class Meta:
        verbose_name = 'ASquareUser'
        verbose_name_plural = 'ASquareUsers'


# -------------------------------@mit--------------------------------
# Temp ASquare User for OTP
class TempASquareUser(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=10, unique=True, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'TempUser'
        verbose_name_plural = 'TempUsers'
