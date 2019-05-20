from django.urls import path
from . import views

app_name = 'formupload'

urlpatterns = [
    path('', views.FileUploadView.as_view(), name='home'),
]