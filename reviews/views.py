# Create your views here.
from reviews.models import Thing, Review
from reviews.forms import ReviewForm
from django.views.generic import *
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count, Sum, Avg
import urllib

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

class ThingDetailView(DetailView):
	model = Thing
	queryset = Thing.objects.all().annotate(Sum('review__rating'), Avg('review__rating'))
	
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
		
