from django.conf import settings

DEFAULT_REVIEWS_SCALE = 4;
DEFAULT_REVIEWS_SCORE_MAP = {
				0 : {
						"label" :"Terrible",
						"color": "CC0000" 
					},
				1 : {
						"label" :"Bad",
						"color": "CC6600" 
					},
				2 : {
						"label" :"Good",
						"color": "99CC00" 
					},
				3 : {
						"label" :"Great",
						"color": "00CC00" 
					}
			}

SCALE = getattr(settings,"REVIEWS_SCALE", DEFAULT_REVIEWS_SCALE)
SCORE_MAP = getattr(settings,"REVIEWS_SCORE_MAP", DEFAULT_REVIEWS_SCORE_MAP)
