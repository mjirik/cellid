from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
# Imaginary function to handle an uploaded file.
# from .imageprocessing import handle_uploaded_file
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import ImageQuatroForm
from .models import ImageQuatro, CellImage
from django.http import Http404
import glob
from django.core.files import File
from django.conf import settings

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
            from . import imageprocessing
            # imageprocessing.quatrofile_processing()
            return redirect('imviewer/home/')
    else:
        form = ImageQuatroForm()
    return render(request, 'imviewer/model_form_upload.html', {
        'form': form
    })


from django.views import generic

class ImageQuatroListView(generic.ListView):
    model = ImageQuatro

class ImageQuatroDetailView(generic.DetailView):
    model = ImageQuatro

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ImageQuatroDetailView, self).get_context_data(**kwargs)
        # Get the blog from id and add it to the context
        context['some_data'] = 'This is just some data'
        datadir = context["imagequatro"].outputdir
        print("get_context_data")
        print(datadir)
        import glob
        filelist = glob.glob(datadir + "/serazeno/*.png")
        filelist.sort()
        imagequatro = super(ImageQuatroDetailView, self).get_object()
        imagequatro.imagequatro_preview=filelist[0]
        imagequatro.save()

        context["cellimages"] = filelist

        return context

def home(request):
    documents = ImageQuatro.objects.all()

    # print("home page render")
    # print(dir(documents))
    # print(documents[0])
    return render(request, 'imviewer/home.html', {'documents': documents})
    pass


def ImageQuatroProcessView(request, pk):
    try:
        iq = ImageQuatro.objects.get(pk=pk)
    except ImageQuatro.DoesNotExist:
        raise Http404("Book does not exist")

    # book_id=get_object_or_404(Book, pk=pk)

    print("imagqquatra processing, pk=" + str(pk))
    from . import imageprocessing
    order2id = imageprocessing.quatrofile_processing(
        multicell_fitc=iq.multicell_fitc.path,
        multicell_dapi=iq.multicell_dapi.path,
        singlecell_fitc=iq.singlecell_fitc.path,
        singlecell_dapi=iq.singlecell_dapi.path,
        outputpath=iq.outputdir
    )

    filelist = glob.glob(op.join(iq.outputdir , "serazeno/*.png"))
    filelist.sort()
    for i, fl in enumerate(filelist):
        cellim = CellImage(imagequatro=iq, penalty=float(i))
        # cellim.image = fl
        flrel = op.relpath(fl, settings.MEDIA_ROOT)
        cellim.image = flrel
        cellim.multicelloverview_id = order2id[i]
        cellim.save()

    mco = op.relpath(op.join(iq.outputdir, "Popisky.png"), settings.MEDIA_ROOT)
    sco = op.relpath(op.join(iq.outputdir, "hledana.png"), settings.MEDIA_ROOT)
    iq.multicell_overview = mco
    iq.singlecell_overview = sco
    iq.save()

    return render(
        request,
        'imviewer/imagequatro_process.html',
        context={'imagequatro': iq, }
    )
