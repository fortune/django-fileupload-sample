
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Create your models here.

def get_upload_to(instance, filename):
    return '{0}/{1}'.format(instance.user.username, filename)


fs = FileSystemStorage()

class FileUploadModel(models.Model):
    """
    Upload されたファイルを表現するモデル
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)

    # データベース上での実体は、ファイルの保存場所を示す可変長文字列（デフォルト最大長は、100）。
    # settings.MEDIA_ROOT で指定されるルートからの相対パスがその文字列になる。
    # ここだと、document.name でそれにアクセスできる。FileField には他にもフィールドがあるが、
    # それは内部的に何らかのメソッドを実行することにより、取得される。たとえば、
    # document.size とするとファイルのサイズが取得できるが、ファイルシステム上からファイルを削除すれば
    # 失敗するし、置換すれば返ってくるサイズが変わる。
    #
    # この Model を save するタイミングでファイルそのものが、所定の場所に保存される。
    document = models.FileField(upload_to=get_upload_to, max_length=200, storage=fs)
    #document = models.FileField(upload_to=get_upload_to, max_length=200)

    uploaded_at = models.DateTimeField(auto_now_add=True)
