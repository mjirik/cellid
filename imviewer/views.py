from django.shortcuts import render

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


