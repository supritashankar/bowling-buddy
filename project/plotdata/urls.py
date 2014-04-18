from django.conf.urls import patterns, url

urlpatterns = patterns('plotdata.views',
    url(r'^homepage/$','homepage'),
    url(r'^compare/(?P<frame1>[1-9])/(?P<frame2>[1-9])/$','data'),
    url(r'^save/(?P<query>[a-zA-Z0-9,&]+)/$','save'),
)
