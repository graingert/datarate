from django.conf.urls.defaults import patterns, include, url
import reviews
# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'datarate.views.home', name='home'),
    # url(r'^datarate/', include('datarate.foo.urls')),

    #Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('django_browserid.urls')),
    (r'', include('reviews.urls')),
    url(r'^sign-out/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^sign-in/$', 'django.contrib.auth.views.login', name="login")
)
