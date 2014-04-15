from django.conf.urls import patterns, url

urlpatterns = patterns('plotdata.views',
    url(r'^homepage/$','homepage'),
    url(r'^(?P<round>[1-5])/$','data'),
)
