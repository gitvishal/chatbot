from django.urls import path

from . import views, views_ajax

app_name = 'master'

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),
	path('hotel/', views.HotelView.as_view(), name='hotel'),
	path('room/', views.RoomView.as_view(), name='room'),
	path('room-booking/<int:room_id>/', views.BookingView.as_view(), name='room-booking'),
	path('room-payment/<int:pk>/', views.PaymentView.as_view(), name='room-payment'),
	path('chatbot-ajax/', views_ajax.ChatbotAjax.as_view(), name='chatbot-ajax'),
	path('room-ajax/', views_ajax.RoomAjax.as_view(), name='room-ajax'),
	path('web-hook/', views.DialogFlowHook.as_view(), name='web-hook'),
	path('success-booking/', views.PaymentSuccess.as_view(), name='success-booking'),
]

