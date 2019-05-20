import os
import pathlib

from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage


# Create your views here.

def simple_upload(request):
    fs = FileSystemStorage()
    #fs = default_storage

    # settings.MEDIA_ROOT 下のファイル一覧を取得し、
    # それを fs.url() で URL に変換して、ダウンロード用 URL のリストをつくる。
    media_root = pathlib.Path(settings.MEDIA_ROOT)
    uploaded_file_list = [fs.url(p.name) for p in media_root.iterdir() if p.is_file()]

    if request.method == 'POST' and 'myfile' in request.FILES:

        # request.POST は辞書型のデータであり、フォームデータが入っている。
        # キーがフィールド名（name 属性の値）であり、値はフィールド値だ。
        print('request.POST: ' + str(request.POST))

        # アップロードされたファイルは、辞書型の request.FILES に格納されている。
        # HTML フォーム内で type="file" となっているフィールドだ。キーが
        # フィールド名（name 属性値）であり、値は、アップロードされたファイルデータになっている。
        # ファイルデータは、サイズが小さければ全体がメモリ上に格納され、一定サイズ以上だと
        # システムの一時ディレクトリ内に一時ファイルとして作成される。
        #
        # サイズや一時ファイルの作成場所は設定可能。
        print('request.FILES: ' + str(request.FILES))

        title = request.POST['title']
        myfile = request.FILES['myfile']

        # myfile.name はクライアント側のファイル名だ。それが
        # settings の MEDIA_ROOT に指定したディレクトリに作成される。
        # したがって、システム上では、MEDIA_ROOT/{myfile.name} という名前で
        # アップロードファイルが作成される。ただし、同名ファイルがすでにあった場合、
        # その名前（ベース名）に _YiVN11y のようなランダムな文字列をつけた名前にして
        # 作成する。save の戻り値はその作成後の名前になる（ MEDIA_ROOT 部分は含まない）。
        #
        # MEDIA_ROOT が未設定だと、プロジェクトルートに作成される。 
        filename = fs.save(myfile.name, myfile)
        print('The return value of fs.save: ' + str(filename))

        # url(filename) の戻り値は、settings の MEDIA_URL を filename の
        # 頭につけたものになる。MEDIA_URL が /hoge/ で、filename が boo.txt なら
        # /hoge/boo.txt になる。
        # URL エスケープされた値になる。
        uploaded_file_url = fs.url(filename)
        print('The return value of fs.url: ' + str(uploaded_file_url))

        return render(request, 'simpleupload/simple_upload.html', {
            'uploaded_file_url': uploaded_file_url,
            'uploaded_file_list': uploaded_file_list})

    return render(request, 'simpleupload/simple_upload.html', {
        'uploaded_file_list': uploaded_file_list})
