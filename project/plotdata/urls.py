from django.conf.urls import patterns, url

urlpatterns = patterns('plotdata.views',
    url(r'^homepage/$','homepage'),
    url(r'^compare/(?P<frame>[0-9])/velocity/$','velocity'),
    url(r'^compare/(?P<frame>[0-9])/distance/$', 'distance'),
    url(r'^compare/(?P<frame>[0-9])/angles/$', 'angles'),
    url(r'^save/(?P<query>[a-zA-Z0-9,&]+)/$','save'),
    url(r'^search/(?P<search_date>\d+)/$', 'search'),
)
