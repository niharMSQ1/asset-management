from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include('users.urls')),
    path('api/', include('servicenow.urls')),
    path('api/', include('freshservice.urls')),
    path('api/', include('jira.urls')),
]
