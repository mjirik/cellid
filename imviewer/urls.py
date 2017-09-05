from django.conf.urls import url

from . import views
from django.contrib.auth.views import login, logout

app_name = 'imviewer'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home/', views.home, name="home"),
    url(r'^images/', views.ImageQuatroListView.as_view(), name="images"),
    url(r'^image-detail/(?P<pk>\d+)$', views.ImageQuatroDetailView.as_view(), name='image-detail'),
    url(r'^login/', login, {"template_name": "imviewer/login.html"}),
    url(r'^logout/', logout, {"template_name": "imviewer/logout.html"}),
    url(r'^upload/', views.model_form_upload, name="model_form_upload"),
    url(r'^register/$', views.register, name='register')
]