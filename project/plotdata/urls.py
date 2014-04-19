from django.conf.urls import patterns, url

urlpatterns = patterns('plotdata.views',
    url(r'^homepage/$','homepage'),
    url(r'^compare/(?P<frame1>[0-9])/(?P<frame2>[0-9])/$','data'),
    url(r'^save/(?P<query>[a-zA-Z0-9,&]+)/$','save'),
    url(r'^search/(?P<search_date>\d+)/$', 'search'),
)
