from django.conf.urls import url

from . import views

app_name = "recipes"
urlpatterns = [
    url(r'^$', 'recipes.views.index', name='index'),
    url(r'^detail/([0-9]+)', 'recipes.views.detail', name='detail')
]