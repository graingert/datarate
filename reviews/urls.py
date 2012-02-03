from django.conf.urls.defaults import *
from reviews import models as m
from django.views import generic as g
from reviews import views as v


urlpatterns = patterns('',
	url(r'^$', g.TemplateView.as_view(template_name="index.html")),
	url(r'^review/(?P<pk>\d+)$', g.DetailView.as_view(model=m.Review), name="review_detail"),
	url(r'^review/$', g.ListView.as_view(model=m.Review)),
	url(r'create-review/$',g.CreateView.as_view(model=m.Review)),
	url(r'^object/(?P<url>\d+)$', v.ReviewableDetailView.as_view(), name="reviewable_detail"),
)
