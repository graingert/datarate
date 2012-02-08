from django.conf.urls.defaults import *
from reviews import models as m
from django.views import generic as g
from reviews import views as v


urlpatterns = patterns('',
	url(r'^$', g.TemplateView.as_view(template_name="index.html")),
	url(r'^review/(?P<pk>\d+)$', g.DetailView.as_view(model=m.Review), name="review_detail"),
	url(r'^review/$', g.ListView.as_view(model=m.Review)),
	url(r'create-review/$',g.CreateView.as_view(model=m.Review)),
	url(r'^things/(?P<slug>[-\w]+)$', v.ThingDetailView.as_view(model=m.Thing), name="thing_detail"),
)
