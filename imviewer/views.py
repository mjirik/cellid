from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
# Imaginary function to handle an uploaded file.
from imageprocessing import handle_uploaded_file

import os.path as op
# Create your views here.

def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    fn = op.abspath(__file__)
    print(fn)
    import html.parser
    fnhtml = html.escape(fn)
              # latest_question_list
    context = {'pth': fn,
               "range110": list(range(1, 10))}
    return render(request, 'imviewer/index.html', context)

@login_required()
def home(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    fn = op.abspath(__file__)
    print(fn)
    import html.parser
    fnhtml = html.escape(fn)
    # latest_question_list
    context = {'pth': fn,
               "range110": list(range(1, 10))}
    return render(request, 'imviewer/index.html', context)


def login_redirect(request):
    return redirect('imviewer/login')


def register(request):
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('imviewer/')
    else:
        form = UserCreationForm()

        args = {'form': form}
        return render(request, 'imviewer/reg_form.html', args)

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UploadFileForm


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})