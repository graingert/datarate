# Create your views here.
from reviews.models import Thing, Review, UserProfile
from django.contrib.auth.models import User
from reviews.forms import ReviewForm, ProfileForm
from django.views.generic import *
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Avg
import urllib
from django import http
from django.utils import simplejson as json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from datarate.django_http_exception import HttpException
import httplib

from thingvalidator import ThingException
	

class PreviewView(TemplateView):
	template_name="index.html"
	
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(PreviewView, self).get_context_data(**kwargs)
		
		things = Thing.objects
		total_scores = things.filter(ci_lower_bound__isnull=False, ci_lower_bound_reversed__isnull=False)
		
		context["best"] = total_scores.order_by("-ci_lower_bound")[:5]
		context["worst"] = total_scores.order_by("-ci_lower_bound_reversed")[:5]
		context["reviews"] = Review.objects.all().order_by("-date_created")[:5]

		return context


class ThingRedirectView(RedirectView):
	permanent = False
	query_string = False
	
	
	def get_redirect_url(self, **kwargs):
		
		if "uri" not in self.request.GET:
			raise http.Http404
		else:
			uri = self.request.GET["uri"]
		
		try:
			thing = Thing.construct_from_uri(uri)

		except ThingException, e:
			raise HttpException(message=e.message, status=httplib.BAD_GATEWAY)
		
		return thing.get_absolute_url() + "." + kwargs["format"]
	
	def get(self, request, *args, **kwargs):
		response = super(ThingRedirectView, self).get(request, *args, **kwargs)
		response['Access-Control-Allow-Origin'] = '*'
		
		return response


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
	
	def render_to_response(self, context, **response_kwargs):
		fmt = self.kwargs.get("format", "html")
		
		if fmt == "json":
			thing = context["object"]
			output = dict(uri = thing.uri,
				total = thing.review__rating__sum,
				average = thing.review__rating__avg,
				count = thing.review__count,
				reviews = self.request.build_absolute_uri(thing.get_absolute_url()),
				ci_lower_bound = self.ci_lower_bound,
			)
			
			response = http.HttpResponse(json.dumps(output),
				content_type='application/json')
				
			response['Access-Control-Allow-Origin'] = '*'
			
			return response
		else:
			return super(ThingDetailView, self).render_to_response(context, **response_kwargs)



class ReviewCreateView(CreateView):
	model = Review
	form_class = ReviewForm

	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(ReviewCreateView, self).get_context_data(**kwargs)
		context["thing"] = Thing.objects.get(slug=self.kwargs["slug"])
		return context
	
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
		
class ReviewUpdateView(UpdateView):
	model = Review
	form_class = ReviewForm
	
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(ReviewUpdateView, self).get_context_data(**kwargs)
		context["thing"] = self.object.reviewed_uri
		return context
	
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(ReviewUpdateView, self).dispatch(*args, **kwargs)
	
	
	#Check to see if the user is the correct user
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.author != request.user:
			return http.HttpResponseForbidden()
		else:
			return super(ReviewUpdateView, self).post(self, request, *args, **kwargs)
			
class ProfileUpdateView(UpdateView):
	model = UserProfile
	form_class = ProfileForm
	queryset = User.objects.all()
		
	def get_object(self):
		user = super(ProfileUpdateView, self).get_object()
		return user.get_profile()
	
	#Check to see if the user is the correct user
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.user != request.user:
			return http.HttpResponseForbidden()
		else:
			return super(ProfileUpdateView, self).post(self, request, *args, **kwargs)
		
class TagCloudView(ListView):
	model = Thing
	queryset = Thing.objects.all().annotate(Sum('review__rating'), Avg('review__rating'), Count('review'))
	template_name="reviews/tagcloud.html"
