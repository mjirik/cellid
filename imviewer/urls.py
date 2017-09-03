from django.conf.urls import url

from . import views
from django.contrib.auth.views import login, logout

app_name = 'imviewer'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home/', login, {"template_name": "imviewer/login.html"}),
    url(r'^login/', login, {"template_name": "imviewer/login.html"}),
    url(r'^logout/', logout, {"template_name": "imviewer/logout.html"}),
    url(r'^register/$', views.register, name='register')
]