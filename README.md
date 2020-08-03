# Django ファイルアップロードのサンプル

以下、４つのサンプルアプリケーションを作成した。

<dl>
    <dt>simpleupload</dt>
    <dd>Django の Form や Model を使わずに生のファイルアップロードを実装する。</dd>
    <dt>formupload</dt>
    <dd>Django の Form クラスを利用した実装。</dd>
    <dt>modelformupload</dt>
    <dd>Django の Model と ModelForm を利用した実装。</dd>
    <dt>azureblobupload</dt>
    <dd>ローカルのファイルシステムではなく、Microsoft の Azure Blob ストレージへアップロードするサンプル。</dd>
</dl>


参考にしたサイト

[ファイルのアップロード](https://docs.djangoproject.com/ja/2.2/topics/http/file-uploads/)

[How to Upload Files With Django](https://simpleisbetterthancomplex.com/tutorial/2016/08/01/how-to-upload-files-with-django.html)

[Advanced Django File Handling](https://www.caktusgroup.com/blog/2017/08/28/advanced-django-file-handling/)

[django-storages: Azure Storage](https://django-storages.readthedocs.io/en/latest/backends/azure.html)


## 環境構築と実行方法

仮想環境を作成し、必要なパッケージをインストールし、テスト用 Web サーバを起動する。

```shell
$ python3 -m venv VENV
$ source VENV/bin/activate
(VENV) $ pip install -r requirements.txt
(VENV) $ python manage.py runserver
```

これで各アプリケーションへのリンクを表示するトップページが表示される。トップページは、単にテンプレートを表示するだけの処理なので、
`django.views.generic.TemplateView` を使い、いちいち View を定義せず、`project/urls.py` に直接書いてしまっている。

```python
path('', TemplateView.as_view(template_name='index.html'), name='index'),
```

## 認証まわりの実装

`simpleupload` 以外の `formupload`, `modelformupload`, `azureblobupload` アプリケーションは、
ログイン済みユーザだけがアクセス可能なように作ってある。

手間を省くために、Django が提供しているログイン、ログアウト用の View である `django.contrib.auth.views.LoginView` と
`django.contrib.auth.views.LogoutView` をそのまま `project/url.py` 中で使用する。

```python
path('login/', LoginView.as_view(template_name='login.html'), name='login'),
path('logout/', LogoutView.as_view(), name='logout'),
```

ログアウトの方は、デフォルトのテンプレートである `registration/logged_out.html` をそのまま使う。ログインの方は
デフォルトテンプレート名である `registration/login.html` は存在しないので、自分で作成し、テンプレート名も変えてある。

ログインを強制するために `formupload`, `modelformupload`, `azureblobupload` の各アプリケーションの View 定義では、
`django.contrib.auth.decorators.login_required` デコレータを View につけている。また、ログイン、ログアウトまわりの
ページ遷移のために `settings` に

```python
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

という設定をしている。これにより、ログインが必要なときは、`LOGIN_URL`、ログアウトしたら `LOGOUT_URL` にリダイレクトさせる。
ログインに成功した場合は、`LOGIN_REDIRECT_URL` にリダイレクトさせるが、next ページが指定されている場合は、そこにリダイレクトする。
`login_required` デコレータによってログインページにリダイレクトされるときに、この next ページがもともとリクエストされたページに
なるようにセットされるのだが、デフォルトの `LoginView` はそれを適切に扱っている。また、自作した `login.html` テンプレートでも
それを処理しているのがわかる。

Django での認証については、[Django の認証とセッションの基礎](https://github.com/fortune/django-auth-session-sample) に
まとめてみた。


## Media ファイル関連の設定

Static なファイルに関する設定を settings モジュールの `STATIC_URL`, `STATIC_ROOT` で設定するように Media ファイル、
つまり、ユーザがアップロードするファイルのための設定を `MEDIA_URL`, `MEDIA_ROOT` でおこなう。

この２つの設定が使われるのは、`DEFAULT_FILE_STORAGE` として `django.core.files.storage.FileSystemStorage` が
使われているときだ（デフォルト）。このとき、アップロード先のルートとして `MEDIA_ROOT` が使用され、ダウンロード用の URL を
作るときに `MEDIA_URL` がプリフィックスとしてパスの先頭につけられる。

本番運用時には、`MEDIA_URL` ではじまるパスは Nginx 等のリバースプロキシで処理して、`MEDIA_ROOT` 下へアクセスするように
しておく必要がある。開発時にこの手間を省くために、Static ファイルのときと同様、`DEBUG=TRUE` で Django 付属の
テスト Web サーバの runserver を使えば、プロジェクトの `urls.py` で

```python
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

を記述しておけば、`MEDIA_URL` ではじまるパスは、`MEDIA_ROOT` ディレクトリ下のファイルへのアクセスとなるようにしてくれる。

`azureblobupload` アプリケーションでは、ローカルファイルシステムではなく、Azure Blob ストレージへアップロードしているので、
`django.core.files.storage.FileSystemStorage` ではなく、別の Storage クラスを使うように `settings.DEFAULT_FILE_STORAGE` で
指定している。そのため、`simpleupload`, `formupload`, `modelformupload` アプリケーションでは、
`django.core.files.storage.FileSystemStorage` を明示的に使うようにしている。

[Advanced Django File Handling](https://www.caktusgroup.com/blog/2017/08/28/advanced-django-file-handling/)


## simpleupload

アップロードされたファイルに直接 `request.FILES` をとおしてアクセスする。ここからアップロード時のファイル名とファイルそのものを
取り出し、`django.core.files.storage.FileSystemStorage` を使って保存する。したがって、`settings.MEDIA_URL`,
`settings.MEDIA_ROOT` が使われる。

## formupload

`simpleupload` とほぼ同じだが、Django の Form 内に `django.forms.FileField` を定義し、それを通して
アップロード時のファイル名とファイルそのものを取り出す。ファイルの保存や URL の生成に `django.core.files.storage.FileSystemStorage` を
使っているのは、`simpleupload` と同じだが、ユーザ名をパスに加えるようにしている。そのため、`settings.MEDIA_ROOT` で
指定したディレクトリにあらかじめユーザ名のディレクトリを作っておかないといけない。

## modelformupload

Django の Model と `django.db.models.FileField` を使う。これにより、Model の save メソッドを実行すれば、
データベースに保存先のパス等が保存されると同時に、ファイルそのものがストレージに保存される。`FileField` はデフォルトでは
`settings.DEFAULT_FILE_STORAGE` を使用する。`azureblobupload` 用にこの設定を変えているので、ローカルの
ファイルシステム上に保存するために、Model 内に `FileField` を定義するとき、オプションで `FileSystemStorage` を
使うように指示している。

Django の通常の Form とその中の `django.forms.FileField` を使ってアップロードファイルを取り出し、それを
Model とその中の `django.db.models.FileField` にセットしてもいいが、ここでは、ModelForm を利用している。
これにより、ModelForm の save メソッドで Model の save メソッドまで実行することができる。

`django.db.models.FileField` をとおして、その下ではたらいている Storage クラスへアクセスする。したがって、
`FileField` の name や size や url にアクセスすると、保存されたファイルの名前やサイズ、ダウンロード用の URL を
取得できる。


## azureblobupload

`modelformupload` では Model 内の `django.db.models.FileField` で明示的に `django.core.files.storage.FileSystemStorage` を
使うように指示したが、ここではそうしていない。したがって、`settings.DEFAULT_FILE_STORAGE` に設定した Storage クラスが
使用される。そこには、

```python
DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
```

のように設定してあるので、Azure の Blob ストレージへとアップロードファイルが転送されて保存される。

[django-storages: Azure Storage](https://django-storages.readthedocs.io/en/latest/backends/azure.html)

この Storage クラスは `settings.MEDIA_URL`, `settings.MEDIA_ROOT` の設定を使わない。代わりに、使用する Azure ストレージの
アカウント名やアカウントキー、コンテナ名などの設定値を `settings` モジュールに定義しておく。

`django.db.models.FileField` の url を通してアクセスする `storages.backends.azure_storage.AzureStorage` の
url() メソッドにバグがあり、返される Azure Blob ストレージへの URL に付加される SAS トークンが無効で、ダウンロードできなかった。
そこで該当のソースを修正して、正しい SAS トークンが生成されるようにした。

https://github.com/jschneier/django-storages/issues/705



## azureblobupload を Shell 環境でテスト

```shell
(VENV) $ python manage.py shell
```

をプロジェクトのトップで実行し、Shell 内でアップロードのテストを手動でやってみる。ユーザの登録と、`settings` で Azure ストレージのアカウント名、アカウントキー、コンテナ名の設定は済んでいるとする。

次のコードでテストできる。

```python
from django.contrib.auth.models import User
from azureblobupload.models import BlobUploadModel
from django.core.files import File

user = User.objects.all()[0]
file = open('project/wsgi.py', 'rb')
wrapped_file = File(file)
blob_upload_model = BlobUploadModel(user=user, description='test', document=wrapped_file)
blob_upload_model.save()    # DB に保存されると同時に Azure Blob にファイルがアップロードされる。

# ローカルのファイルを 'project/wsgi.py' で読み出しており、アップロード時にユーザ名をパスの先頭に
# 入れるように models.py で実装しているのでこのようになる。
blob_upload_model.document.name     # 'tomita/project/wsgi.py'

# settings.AZURE_CONTAINER = 'tomita'
# settings.AZURE_LOCATION = 'media'
#
# のように定義してあれば、URL はこのようになる。
# settings.AZURE_URL_EXPIRATION_SECS で指定した秒数だけ有効な SAS トークン付きの URL が生成され、
# その間だけダウンロードが可能だ。
blob_upload_model.document.url      # https://xxxxxxx.blob.core.windows.net/tomita/media/tomita/project/wsgi.py?se=2019-05-29T10%3A24%3A52Z&sp=r&sv=2018-11-09&sr=b&sig=4V5JktU4oHUVtTt9u85jkYmCsJnQ2iqegfleyfa6Ad0%3D
```

## FileField に登録されたファイルの削除と、Model の関係

FileField に登録されたファイルを削除するには、`FileField.delete` メソッドを実行する。そうすると、基礎にある Storage クラスの `delete` メソッドが呼び出されて、ファイルを削除する。削除後の FileField は `None` になるのだが、それが DB に反映されるかどうかは `FileField.delete` メソッドにわたす `save` 引数による（デフォルトは `True`）。

`modelformupload` アプリを shell 環境で実行してこのことを試してみる。

```python
from django.contrib.auth.models import User
from modelformupload.models import FileUploadModel
from django.core.files import File

user = User.objects.all()[0]
file = open('project/wsgi.py', 'rb')
wrapped_file = File(file)
model = FileUploadModel(user=user, description='test', document=wrapped_file)
model.save()    # DB に保存されると同時にファイルストレージにファイルがアップロードされる。

doc = model.document
doc.name    # 'admin/project/wsgi.py'
doc.url     # '/media/admin/project/wsgi.py'
doc.path    # '/Users/kazu/Documents/samples/django_samples/django-fileupload-sample/uploaded_files/admin/project/wsgi.py'

doc.storage # <django.core.files.storage.FileSystemStorage object at 0x10663aac8>
doc.storage.exists(doc.name)    # True
doc.storage.exists(doc.path)    # True
doc.storage.exists('hoge/foo')  # False
doc.storage.exists(doc.url)     # django.core.exceptions.SuspiciousFileOperation: The joined path (/media/admin/project/wsgi.py) is located outside of the base path component (/Users/kazu/Documents/samples/django_samples/django-fileupload-sample/uploaded_files)

doc.delete(save=False)
doc.name    # None
doc.storage.exists('admin/project/wsgi.py')    # False
doc.storage.exists('admin/project')    # True

# FileField.delete メソッドによりファイルが削除され、ファイルに関連するフィールドもクリアされているが、
# save=False で実行したので、DB には反映されていない。したがって、

m = FileUploadModel.objects.get(id=model.id)
m.document.name     # 'admin/project/wsgi.py'

# のようになる。

model.save()    # これで DB に反映される。
m = FileUploadModel.objects.get(id=model.id)
m.document.name # '' 空文字列

# doc.delete(save=True) （デフォルト）であれば、ファイルを削除し、model が DB に反映される。
```


## Model 削除時に FileField に登録されたファイルを削除する

`Model` を削除しただけでは、`FileField` に登録されているファイルはそのまま残る。`Model` 削除のタイミングでファイルも削除するにはいくつか方法があるようだが、`post_delete` シグナルでファイル削除のハンドラを登録する方法がある。

`azureblobupload` アプリの Shell 環境でこのことを試してみる。

```python
from django.contrib.auth.models import User
from azureblobupload.models import BlobUploadModel
from django.core.files import File

from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=BlobUploadModel)
def delete_blob(sender, instance, **kwargs):
    instance.document.delete(save=False)    # save=False の指定は必須

user = User.objects.all()[0]
file = open('project/wsgi.py', 'rb')
wrapped_file = File(file)
model = BlobUploadModel(user=user, description='test', document=wrapped_file)
model.save()    # DB に保存されると同時に Azure Blob にファイルがアップロードされる。

model.document.storage.exists(model.document.name)  # True

model.delete()  # DB から Model が削除され、Blob も削除される。

```

上のコードの `delete_blob` 関数内で、`FileField.delete` メソッドに `save=False` を指定するのはものすごく重要だ。デフォルトの `save=True` だと、ファイル削除後に `Model` を save するので、削除後の Model を復活させてしまうからだ。
