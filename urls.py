from django.conf.urls.defaults import patterns, include, url
from reviews import models as m
from django.views import generic as g
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
)

urlpatterns += patterns('',
	url(r'^$', g.TemplateView.as_view(template_name="index.html")),
	url(r'^review/(?P<pk>\d+)$', g.DetailView.as_view(model=m.Review), name="review_detail"),
	url(r'^review/$', g.ListView.as_view(model=m.Review)),
	url(r'create-review/$',g.CreateView.as_view(model=m.Review)),
)
