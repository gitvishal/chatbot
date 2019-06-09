from django import forms
from bootstrap_datepicker_plus import DateTimePickerInput
from django.conf import settings
from .models import *
import requests

class ChatbotForm(forms.Form):
	question = forms.CharField(label='question')
	chatbot_session_id = forms.CharField(label='chatbot session')

def goa_cities():
	url = '%s/api/city/' % (settings.CHOWGULE_HOTEL_API,)
	req = requests.get(url=url)
	req.raise_for_status()
	return [(None, '-----choose city')] + list(req.json().items())

def goa_room_type():
	url = '%s/api/room-type/' % (settings.CHOWGULE_HOTEL_API,)
	req = requests.get(url=url)
	req.raise_for_status()
	return [(None, '-----choose room type')] + list(req.json().items())

class HotelSearchForm(forms.Form): 
	city = forms.ChoiceField(
		choices=[(None, '-----choose room type')], 
		required=False
	)
	room_type = forms.ChoiceField(
		choices=[(None, '-----choose room type')], 
		required=False
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['city'].choices = goa_cities()
		self.fields['room_type'].choices = goa_room_type()


def get_booking_form(last_booking):
	class BookingForm(forms.ModelForm):

		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.fields['check_in'].widget.attrs['class'] = 'form-control'
			self.fields['days'].widget.attrs['class'] = 'form-control'
			self.fields['user'].widget = forms.HiddenInput()
			self.fields['status'].widget = forms.HiddenInput()
			self.fields['room_id'].widget = forms.HiddenInput()

		class Meta(object):
			model = Booking
			fields = '__all__'

			widgets = {
				'check_in': DateTimePickerInput(options={"minDate":str(last_booking),}),
			}

	return BookingForm

class PaymentForm(forms.Form):
	card_holder_name = forms.CharField(label='Name on Card', )
	card_number = forms.CharField(label='Card Number', )
	expiry_month = forms.ChoiceField(
		choices=[
			(None, 'Month'),
			("01", 'Jan (01)'),
			("02", 'Feb (02)'),
			("03", 'Mar (03)'),
			("04", 'Apr (04)'),
			("05", 'May (05)'),
			("06", 'June (06)'),
			("07", 'July (07)'),
			("08", 'Aug (08)'),
			("09", 'Sep (09)'),
			("10", 'Oct (10)'),
			("11", 'Nov (11)'),
			("12", 'Dec (12)'),
		], 
	)
	expiry_year = forms.ChoiceField(
		choices=[
			("19", '2019'),
			("20", '2020'),
			("21", '2021'),
			("22", '2022'),
			("23", '2023'),
			("24", '2024'),
			("25", '2025'),
			("26", '2026'),
			("27", '2027'),
			("28", '2028'),
		], 
	)
	cvv = forms.CharField(label='Card CVV', )
	booking_id = forms.ModelChoiceField(queryset = Booking.objects.all(), widget=forms.HiddenInput())

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['expiry_year'].widget.attrs['class'] = 'form-control'
		self.fields['expiry_month'].widget.attrs['class'] = 'form-control'
		self.fields['cvv'].widget.attrs['class'] = 'form-control'
		self.fields['cvv'].widget.attrs['placeholder'] = 'Security Code'
		self.fields['card_holder_name'].widget.attrs['class'] = 'form-control'
		self.fields['card_holder_name'].widget.attrs['placeholder'] = "Card Holder's Name"
		self.fields['card_number'].widget.attrs['class'] = 'form-control'
		self.fields['card_number'].widget.attrs['placeholder'] = 'Debit/Credit Card Number'