# myproject/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('store.urls')),  # Pastikan untuk menggunakan prefix 'api/' untuk memisahkan rute API
]
