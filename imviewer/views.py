from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
# Imaginary function to handle an uploaded file.
# from .imageprocessing import handle_uploaded_file
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import ImageQuatroForm
from .models import ImageQuatro

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
def not_home_anymore(request):
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


def model_form_upload(request):
    if request.method == 'POST':
        form = ImageQuatroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('imviewer/home/')
    else:
        form = ImageQuatroForm()
    return render(request, 'imviewer/model_form_upload.html', {
        'form': form
    })

def home(request):
    documents = ImageQuatro.objects.all()
    print("home page render")
    print(dir(documents))
    return render(request, 'imviewer/home.html', {'documents': documents})
    pass
