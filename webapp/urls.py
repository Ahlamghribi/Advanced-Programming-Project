from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('qcm_app.urls')),  # Direct to the qcm_app's URLs
]
