from django.urls import path
from .views import *


urlpatterns = [
    path('api/', get_hardware_details),

]