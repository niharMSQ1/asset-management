from django.urls import path
from .views import *

urlpatterns = [
    path("get-and-save-hardware-assets/", get_hardware_details)
]