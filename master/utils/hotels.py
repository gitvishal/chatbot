import requests
from django.conf import settings
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string

api_url = '%s/%s' % (settings.CHOWGULE_HOTEL_API, 'api/v1/{search_params}room/')

def chowgule_hotel_rendering_api_call(url, search=None):
	req = requests.get(url='%s?s=%s' % (url, search) if search else url)
	req.raise_for_status()
	return req.json()

def rooms(city=None, room_type=None, search=None):
	search_params = '{city}{room_type}'.format(
		city='city-%s/' % (city,) if city else '',
		room_type='type-%s/' % (room_type,) if room_type else '',
	)
	url = api_url.format(search_params=search_params)
	return chowgule_hotel_rendering_api_call(url, search)


def detail_room(room):
	return {
		'room_details':room,
		'hotel': chowgule_hotel_rendering_api_call(room['hotel'], None),
		'images': [chowgule_hotel_rendering_api_call(url, None) for url in room['roomimages_room']]
	}

def authenticate(username=None, password=None):
	url = '%s/api/obtain-auth-token/' % (settings.CHOWGULE_HOTEL_API,)
	req = requests.post(url=auth_url, json={
		'username':settings.HOTEL_USERNAME, 
		'password':settings.HOTEL_PASSWORD
		}
	)
	req.raise_for_status()
	return req.json()

def booking_payment(form, user):
	booking = form.cleaned_data['booking_id']
	auth = authenticate(username=username, password=password)
	headers = {'Authorization': 'Token {token}'.format(token=auth['token'])}

	data = {
		'check_in':booking.check_in,
		'check_out':booking.check_in + timedelta(days=booking.days),
		'room':booking.room_id,
		'created_by':auth['user_id'],
		'payment':{'meta_data':form.cleaned_data},
		'merchants_user_email':user.email,
	}
	url = '%s/api/v1/reservation' % (settings.CHOWGULE_HOTEL_API,)
	req = requests.post(url=auth_url, json={})
	req.raise_for_status()
	return req.json()

def send_success_mail(username, transaction_id, amount):
	user_detail = {
		'username':username, 
		'transaction_id':transaction_id, 
		'amount':amount
	}
	msg_plain = render_to_string('master/email/success.txt', user_detail)
	msg_html = render_to_string('master/email/success.html', user_detail)
	email = send_mail(
		'Successfull booking of hotel',
		msg_plain,
		settings.FROM_EMAIL,
		[user.email,],
		html_message=msg_html, 
		fail_silently=True
	)
	return email