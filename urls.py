from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^s3/(?P<bucket>[\w\-\.]+)/(?P<path>.*)/$', 'buckets.s3.views.list', name='s3_path'),
    url(r'^s3/(?P<bucket>[\w\-\.]+)/$', 'buckets.s3.views.list', name='s3_bucket'),
    url(r'^s3/$', 'buckets.s3.views.bucket_list', name='s3_bucket_list'),
    url(r'^$', 'django.views.generic.simple.redirect_to', {'url': '/s3/'}),
    url(r'^', include('googleauth.urls')),
    url(r'^', include('mediasync.urls')),
)
