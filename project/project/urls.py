from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^charts/',include('charts.urls')),
    url(r'^plotdata/', include('plotdata.urls')),
)