"""ekonomicka URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import auth
from core import forms
import core.views
import django.contrib.auth.views

urlpatterns = [
    url(r'^team/create/', core.views.create_team, name = 'team/create'),
    url(r'^team/', core.views.team, name = 'team'),
    url(r'^login/$', auth.views.login, {'template_name' : 'core/login.html', 'authentication_form' : forms.AuthenticationForm }, name='login'),
    url(r'^logout/$', auth.views.logout, { 'template_name' : 'core/logout.html' }, name='logout'),
    url(r'^control/start', core.views.control_start, name = 'control/start'),
    url(r'^control/', core.views.control, name = 'control'),
    url(r'^wait/', core.views.wait_to_start, name = 'wait'),
    url(r'^entity_detail/(\d+)', core.views.entity_detail, name = 'entity_detail'),
    url(r'^messages/', core.views.messages, name='messages'),
    url(r'^inventory/', core.views.inventory, name='inventory'),
    url(r'^$', core.views.router, name = 'router'),
]
