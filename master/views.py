from django.shortcuts import render
from master.utils.hotels import (
	rooms, detail_room, send_success_mail,
	chowgule_hotel_rendering_api_call, booking_payment
)
from django.template.response import TemplateResponse
from django.views.generic import TemplateView, View, FormView 
from django.views.generic.edit import UpdateView, CreateView 
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from master.forms import HotelSearchForm, get_booking_form, PaymentForm
from django.conf import settings
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.dateparse import parse_datetime
from .models import Booking
import uuid
import json
import requests

@method_decorator([csrf_exempt, ], name='dispatch')
class DialogFlowHook(View):
	search_pattern = 'search result:<a href="%s" class="btn btn-info" role="button">view search data</a>'
	def post(self, request, *args, **kwargs):
		data = json.loads(request.body)

		print(data.get('queryResult'))

		try:
			action = data.get('queryResult').get('action')
		except AttributeError:
			return JsonResponse({
				'fulfillmentText': 'error while fetching',
				}
			)

		search_url = reverse_lazy('master:hotel')

		if action == 'city-hotel':
			search_url = '%s?s=%s' %(search_url, ' '.join(data['queryResult']['parameters'].values()))  

			return JsonResponse({
				'fulfillmentText': self.search_pattern % (search_url),
				}
			)



class HomeView(TemplateView):
	template_name = 'master/home.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['chatbot_session_id'] = uuid.uuid4().hex
		return context

class HotelView(TemplateView):
	template_name = 'master/hotel.html'

	def get_room_list(self, rooms):
		return [ detail_room(room) for room in rooms ]

	def call_room_api(self):
		city = self.request.GET.get('city')
		room_type = self.request.GET.get('room_type')
		search = self.request.GET.get('s')
		return  rooms(city, room_type, search)
		
	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		search = self.request.GET.get('s')
		city = self.request.GET.get('city')
		room_type = self.request.GET.get('room_type')
		rooms_api = self.call_room_api()
		context['rooms_count'] = rooms_api['count']
		previous = rooms_api['previous']
		next_page = rooms_api['next']
		context['rooms_previous'] = '%s&s=%s' % (previous, search) if previous else previous
		context['rooms_next'] = '%s&s=%s' % (next_page, search) if next_page else next_page
		context['rooms'] = self.get_room_list(rooms_api['results'])
		context['form'] = HotelSearchForm({'city':city, 'room_type':room_type})
		context['hotel_api_url'] = settings.CHOWGULE_HOTEL_API
		return context

class RoomView(TemplateView):
	template_name = 'master/room.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['room'] = detail_room(chowgule_hotel_rendering_api_call(self.request.GET.get('room_url')))
		return context

@method_decorator([login_required,], name='dispatch')
class BookingView(CreateView):
	template_name = 'master/booking.html'
	model = Booking
	room_id = None

	def get_form_class(self, *args, **kwargs):
		url = '%s/api/last-reservation/%d' % (settings.CHOWGULE_HOTEL_API, self.room_id)
		req = requests.get(url=url)
		req.raise_for_status()
		return get_booking_form(parse_datetime(req.json()['last_checkout']))

	def get_success_url(self, *args, **kwargs):
		return reverse_lazy("master:room-payment", kwargs={'pk':self.object.pk})

	def get_initial(self):
		return {
		'user': self.request.user, 
		'room_id': self.room_id, 
		'status':Booking.BOOKING_INPROGRESS
	}

	def get(self, room_id, *args, **kwargs):
		self.room_id = room_id
		return super().get(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['room_id'] = self.room_id
		return context

	def post(self, room_id, *args, **kwargs):
		self.room_id = room_id
		return super().post(*args, **kwargs)

@method_decorator([login_required,], name='dispatch')
class PaymentView(FormView):
	template_name = 'master/payment.html'
	error_template_name = 'master/payment_error.html'
	form_class = PaymentForm
	success_url = reverse_lazy('master:success-booking')

	def get_initial(self):
		return { 'booking_id': self.booking_id, }

	def form_valid(self, form):
		booking = form.cleaned_data['booking_id']
		try:
			payment = booking_payment(form, self.request.user)
			booking.status = Booking.BOOKING_SUCCESS
			booking.transaction_id = payment['payment']['transaction_id']
			booking.save()
			email = send_success_mail(
				self.request.user.username,
				booking.transaction_id,
				payment['payment']['price']
			)
		except Exception as e:
			booking.status = Booking.BOOKING_FAILED
			booking.save()
			return TemplateResponse(
				self.request, 
				self.error_template_name,
				{'error':str(e)}
			)

		return super().form_valid(form)

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context['booking_id'] = self.booking_id
		return context

	def get(self, pk, *args, **kwargs):
		self.booking_id = pk
		return super().get(*args, **kwargs)

	def post(self, pk, *args, **kwargs):
		self.booking_id = pk
		return super().post(*args, **kwargs)

class PaymentSuccess(TemplateView):
	template_name = 'master/payment_success.html'
