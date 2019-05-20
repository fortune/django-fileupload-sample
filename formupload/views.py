import os
import pathlib

from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import FileUploadForm


def get_uploaded_file_list(fs, username):
    """
    ユーザがアップロード済みのファイルをダウンロードするための URL 一覧を取得する。
    path の下に username というディレクトリがあると想定し、その下にあるファイルの一覧をつくる。

    fs -- URL 生成に使用するファイルストレージ
    """
    root = pathlib.Path(os.path.join(settings.MEDIA_ROOT, username))
    return [fs.url(os.path.join(username, p.name)) for p in root.iterdir() if p.is_file()]


# Create your views here.

@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class FileUploadView(View):
    template_name = 'formupload/form_upload.html'

    def get(self, request, *args, **kwargs):
        #fs = default_storage
        fs = FileSystemStorage()
        uploaded_file_list = get_uploaded_file_list(fs, request.user.username)

        context = {
            'form': FileUploadForm(),
            'uploaded_file_list': uploaded_file_list,
        }
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        #fs = default_storage
        fs = FileSystemStorage()
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            description = form.cleaned_data['description']
            myfile = form.cleaned_data['myfile']
            fs.save(os.path.join(request.user.username, myfile.name), myfile)

            # メッセージフレームワーク（MessageMiddleware）を使って、アップロード成功のメッセージを出すべき。
            return redirect('formupload:home')
        else:
            uploaded_file_list = get_uploaded_file_list(fs, request.user.username)
            context = {
                'form': form,
                'uploaded_file_list': uploaded_file_list,
            }

            return render(request, self.template_name, context)

