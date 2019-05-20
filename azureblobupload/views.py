from django.shortcuts import render, redirect

from django.views.generic import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .forms import BlobUploadForm
from .models import BlobUploadModel


# Create your views here.

@method_decorator(login_required, name='get')
@method_decorator(login_required, name='post')
class BlobUploadView(View):
    template_name = 'azureblobupload/azureblob_upload.html'

    def get(self, request, *args, **kwargs):
        uploaded_file_list = BlobUploadModel.objects.filter(user=request.user)

        context = {
            'form': BlobUploadForm(),
            'uploaded_file_list': uploaded_file_list,
        }
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        form = BlobUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # ModelForm の save() メソッドを実行すれば、基礎にある Model の save も
            # 実行されて、データベースに保存される。しかし、FileUploadForm の基礎にある
            # FileUploadModel には Form にはない user があるので、それをセットしてから
            # 実際に DB に保存しなければならない。
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            return redirect('azureblobupload:home')
        else:
            uploaded_file_list = BlobUploadModel.objects.filter(user=request.user)
            context = {
                'form': form,
                'uploaded_file_list': uploaded_file_list,
            }
            return render(request, self.template_name, context)
