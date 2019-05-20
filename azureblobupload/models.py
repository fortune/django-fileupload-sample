from django.db import models
from django.conf import settings
from django.core.files.storage import default_storage


# Create your models here.

def get_upload_to(instance, filename):
    return '{0}/{1}'.format(instance.user.username, filename)



class BlobUploadModel(models.Model):
    """
    Upload されたファイルを表現するモデル
    """

    # Azure ストレージへ格納可能なパスの最大長を取得する。
    # DEFAULT_FILE_STORAGE としてこのメソッドをサポートしている Azure Blob 用のクラスが使用されていることが前提。
    MAX_LENGTH = default_storage.get_name_max_len()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to=get_upload_to, max_length=MAX_LENGTH)
    uploaded_at = models.DateTimeField(auto_now_add=True)
