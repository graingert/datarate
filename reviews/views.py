# Create your views here.
from reviews.models import *
from reviews.forms import ReviewForm
from django.views.generic import *
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count
import urllib

class ThingDetailView(DetailView):
	model = Thing
	
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(ThingDetailView, self).get_context_data(**kwargs)
		context["histogram"] = context["object"].review_set.values('rating').order_by('-rating').annotate(count = Count('rating'))
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
		
