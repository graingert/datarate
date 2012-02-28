from django.forms import ModelForm
from models import Review

from rays.widgets import RangeInput

class ReviewForm(ModelForm):
	class Meta:
		model = Review
		exclude = ("author",)
		widgets = {
			'rating': RangeInput(),
		}
