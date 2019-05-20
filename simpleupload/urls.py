from django.urls import path
from . import views

app_name = 'simpleupload'

urlpatterns = [
    path('', views.simple_upload, name='home'),
]