from django.conf.urls import url
import auctions.views

urlpatterns = [
    url(r'^$', auctions.views.white_list, name = 'user'),
]
