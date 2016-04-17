from django.conf.urls import url
import tokens.views

urlpatterns = [
    url(r'^print$', tokens.views.token_print, name='print'),
    url(r'^$', tokens.views.token_input, name='input'),
]
