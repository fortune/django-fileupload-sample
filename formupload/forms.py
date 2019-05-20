from django import forms

class FileUploadForm(forms.Form):
    description = forms.CharField(label='説明', max_length='30', required=False)
    myfile = forms.FileField(label='アップロードファイル')

