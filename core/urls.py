from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('progress/', progress, name='progress'),
    path('download/<str:filename>', download_file, name='download_file'),
]