from django.conf.urls import url
import auctions.views

urlpatterns = [
    url(r'^create$', auctions.views.create_auction, name = 'create'),
    url(r'^detail/(?P<id>\d+)', auctions.views.detail, name = 'detail'),
    url(r'^$', auctions.views.white_list, name = 'user'),
]
