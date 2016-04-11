from django.conf.urls import url
import tokens.views

urlpatterns = [
    url(r'^$', tokens.views.token_input, name='input'),
]
