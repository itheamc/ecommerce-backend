from django.urls import path
from . import views

urlpatterns = [
    path('supporting-info', views.get_all_supporting_information, name='get_all_supporting_information'),
]
