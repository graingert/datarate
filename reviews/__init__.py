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
DEFAULT_EMAIL_WHITELIST = ("ecs.soton.ac.uk", "soton.ac.uk")
		
SCALE = getattr(settings,"REVIEWS_SCALE", DEFAULT_REVIEWS_SCALE)
SCORE_MAP = getattr(settings,"REVIEWS_SCORE_MAP", DEFAULT_REVIEWS_SCORE_MAP)


EMAIL_WHITELIST = getattr(settings, "AUTH_EMAIL_DOMAIN_WHITELIST", DEFAULT_EMAIL_WHITELIST)

def DEFAULT_EMAIL_VALIDATOR(email):
	if email.rsplit('@', 1)[0] in EMAIL_WHITELIST:
		return True, "Valid email"
		
	return False, "Sorry you need to use an email address ending in one of: {email_whitelist}".format(email_whitelist = " ".join(EMAIL_WHITELIST))

EMAIL_VALIDATOR = getattr(settings,"AUTH_EMAIL_VALIDATOR", DEFAULT_EMAIL_VALIDATOR)
