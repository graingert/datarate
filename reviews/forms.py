from django.forms import ModelForm, HiddenInput
from models import Review

from rays.widgets import RangeInput


class ReviewForm(ModelForm):
	class Meta:
		model = Review
		exclude = ("author",)
		widgets = {
			'rating': RangeInput(min_value=-3, max_value=3, step=2), #uses 4 states preventing any "on the fence choices"
			'reviewed_uri' : HiddenInput(),
		}
