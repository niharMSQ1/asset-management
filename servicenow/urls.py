from django.urls import path
from .views import *

urlpatterns = [
    path("get-and-save-hardware-assets/", get_hardware_details_and_save),
    path("get-hardware-assets_and_save/", get_hardware_details),
    path("objects/", get_objects_by_org_id, name="get_objects_by_org_id"),
    # path("get-zoho-access-refresh-tokens/", generate_access_refresh_token_zoho),
    # path("refresh_zoho_access/", refresh_zoho_access_token)
]