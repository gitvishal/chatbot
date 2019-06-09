from . import forms
from django.http import JsonResponse
from django.views.generic.edit import FormView
from master.utils.hotels import rooms, detail_room, chowgule_hotel_rendering_api_call
from master.views import HotelView
from master.utils import dialogflow
from django.utils import timezone

class ChatbotAjax(FormView):
	template_name = 'master/inclusion/conversation.html'
	form_class = forms.ChatbotForm

	def form_valid(self, form):
		if self.request.is_ajax():
			context = self.get_context_data()
			dialogflow_response = dialogflow.dialogflow_call(
				form.cleaned_data['chatbot_session_id'], 
				form.cleaned_data['question']
			)
			context['user_question'] = dialogflow_response['query_text']
			context['chatbot_answer'] = dialogflow_response['fulfillment_text']
			context['current_time'] = timezone.localtime(timezone.now())
			
			return JsonResponse({
				'conversation': str(self.render_to_response(context).rendered_content),
			})


class RoomAjax(HotelView):
	template_name = 'master/inclusion/room.html'

	def call_room_api(self):
		return  chowgule_hotel_rendering_api_call(self.request.GET.get('room_url'), self.request.GET.get('s'))

	def get(self, *args, **kwargs):
		if self.request.is_ajax():
			response = super().get(*args, **kwargs)

			return JsonResponse({
				'room_data': str(self.render_to_response(response.context).rendered_content),
			})
