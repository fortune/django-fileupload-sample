from django.urls import path
from . import views

app_name = 'azureblobupload'

urlpatterns = [
    path('', views.BlobUploadView.as_view(), name='home'),
]