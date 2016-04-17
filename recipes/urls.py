from django.conf.urls import url

from . import views

app_name = "recipes"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^detail/([0-9]+)', views.detail, name='detail')
]