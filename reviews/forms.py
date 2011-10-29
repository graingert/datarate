from django import forms as f
import models as m

class ReviewForm(f.ModelForm):
	class Meta:
		model = m.Review
