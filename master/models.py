from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

# Create your models here.

@python_2_unicode_compatible
class Booking(models.Model):
	BOOKING_FAILED = 'failed'
	BOOKING_SUCCESS = 'success'
	BOOKING_INPROGRESS = 'inprogress'

	BOOKING_STATUS = (
		(None, '---- booking status ----'),
		(BOOKING_FAILED, 'Failed'), 
		(BOOKING_SUCCESS, 'Success'),
		(BOOKING_INPROGRESS, 'Inprogress'),

	)
	user = models.ForeignKey(User, related_name='%(class)s_user', on_delete=models.CASCADE)
	check_in = models.DateTimeField()
	days = models.IntegerField()
	transaction_id = models.CharField(max_length=100, blank=True, null=True) 
	status = models.CharField(max_length=100,  choices=BOOKING_STATUS, default=BOOKING_INPROGRESS)
	room_id = models.IntegerField()

	def __str__(self):
		return self.status
