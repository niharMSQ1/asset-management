from django.urls import path
from .views import *

urlpatterns = [
    path("ask/",chatapp_response)
]