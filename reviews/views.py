# Create your views here.
from reviews.models import *
from django.views.generic import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import urllib

class ThingDetailView(DetailView):
	model = Thing


class ReviewCreateView(CreateView):
	model = Review
	
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(ReviewCreateView, self).dispatch(*args, **kwargs)
