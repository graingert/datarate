# Create your views here.
from reviews.models import Thing, Review
from reviews.forms import ReviewForm
from django.views.generic import *
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Avg
import urllib
from django import http
from django.utils import simplejson as json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
	

class PreviewView(TemplateView):
	template_name="index.html"
	
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(PreviewView, self).get_context_data(**kwargs)
		
		things = Thing.objects
		total_scores = things.annotate(Sum('review__rating'))
		
		context["best"] = total_scores.order_by("-review__rating__sum")[:5]
		context["worst"] = total_scores.order_by("review__rating__sum")[:5]
		context["reviews"] = Review.objects.all().order_by("-date_created")[:5]
				
		return context

class ThingRedirectView(RedirectView):
	permanent = False
	query_string = False
	
	def get_redirect_url(self, **kwargs):
		uri = self.request.GET["src"]
		
		#TODO: Try to create object if it does not exist rather than 404
		
		return get_object_or_404(Thing, uri=uri).get_absolute_url() + "." + kwargs["format"]


class ThingDetailView(DetailView):
	model = Thing
	queryset = Thing.objects.all().annotate(Sum('review__rating'), Avg('review__rating'), Count('review'))
	
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(ThingDetailView, self).get_context_data(**kwargs)
		
		reviews = context["object"].review_set
				
		paginator = Paginator(reviews.all().order_by("date_created"), 10)
		
		page = self.request.GET.get('page', 1)
		
		try:
			context["reviews"] = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			context["reviews"] = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			context["reviews"] = paginator.page(paginator.num_pages)
		
		return context
	
	def render_to_response(self, context):
		fmt = self.kwargs.get("format", "html")
		
		if fmt == "json":
			thing = context["object"]
			output = dict(src = thing.uri,
				total = thing.review__rating__sum,
				average = thing.review__rating__avg,
				count = thing.review__count
			)
			
			return http.HttpResponse(json.dumps(output),
				content_type='application/json')
		else:
			return super(ThingDetailView, self).render_to_response(context)



class ReviewCreateView(CreateView):
	model = Review
	form_class = ReviewForm

	
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(ReviewCreateView, self).dispatch(*args, **kwargs)
		
	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.author = self.request.user
		self.object.save()
		return super(ReviewCreateView, self).form_valid(form)
		
	def get_initial(self):
		self.initial["reviewed_uri"] = Thing.objects.get(slug=self.kwargs["slug"])
		return self.initial
		
