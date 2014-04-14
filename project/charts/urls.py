from django.conf.urls import patterns, url

urlpatterns = patterns('charts.views',
    url(r'^demo/$','demo'),
    url(r'^demo1/$', 'demo1'),
)
