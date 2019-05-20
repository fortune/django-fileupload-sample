from django.urls import path
from . import views

app_name = 'modelformupload'

urlpatterns = [
    path('', views.FileUploadView.as_view(), name='home'),
]