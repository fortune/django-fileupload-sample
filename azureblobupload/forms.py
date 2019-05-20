from django import forms
from .models import BlobUploadModel


class BlobUploadForm(forms.ModelForm):
    class Meta:
        model = BlobUploadModel
        fields = ('description', 'document')

