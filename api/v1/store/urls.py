from django.urls import path, re_path
from api.v1.common import views as common_views
from . import views

urlpatterns = [
    path('register', views.register_a_seller, name='register-seller'),
    path('login', views.seller_or_staff_login, name='seller-login'),
    path('verify_otp', views.seller_otp_verify, name='seller-otp-verify'),
    path('categories', common_views.get_store_categories, name='store_categories'),
    path('list', views.get_stores, name='all_stores'),
    path('add', views.add_a_store, name='add_store'),
    re_path(r'update/(?P<store_id>\d+)?', views.update_a_store, name='update_store'),
    re_path(r'get/(?P<store_id>\d+)?', views.get_a_store, name='get_store'),
    path('add_staff', views.add_store_staff, name='add_store_staff'),
    re_path(r'staff/(?P<staff_id>\d+)?', views.get_store_staff, name='store_staff'),
]
