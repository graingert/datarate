from django.conf.urls.defaults import *
from reviews import models as m
from django.views import generic as g
from reviews.views import ReviewCreateView, ThingDetailView, PreviewView, ThingRedirectView, ReviewUpdateView


urlpatterns = patterns('',
	url(r'^$', PreviewView.as_view()),
	url(r'^review/(?P<pk>\d+)$', g.DetailView.as_view(model=m.Review), name="review_detail"),
	url(r'^review/(?P<pk>\d+)/edit$',ReviewUpdateView.as_view(), name="edit-review"),
	url(r'^review/$', g.ListView.as_view(model=m.Review, paginate_by=10), name="review"),
	url(r'^thing\.(?P<format>[\w]+)$', ThingRedirectView.as_view(), name="get_based_thing_view"),
	url(r'^thing/$', g.ListView.as_view(model=m.Thing, paginate_by=10), name="thing"),
	url(r'^thing/(?P<slug>[-\w]+)/create-review$',ReviewCreateView.as_view(), name="create-review"),
	url(r'^thing/(?P<slug>[-\w]+)(\.(?P<format>[\w]+))?$', ThingDetailView.as_view(), name="thing_detail"),
)
