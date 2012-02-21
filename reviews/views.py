# Create your views here.
from reviews.models import *
from reviews.forms import ReviewForm
from django.views.generic import *
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import urllib

class ThingDetailView(DetailView):
	model = Thing


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
		
