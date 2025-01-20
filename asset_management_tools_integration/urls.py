from django.urls import path
from .views import *

urlpatterns = [
    path("get-and-save-hardware-assets/", get_hardware_details),
    path("objects/", get_objects_by_org_id, name="get_objects_by_org_id"),
    path("validate_tool/", validate_tool_credentials)
]