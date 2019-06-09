from django.contrib import admin
from master.models import *

@admin.register(Booking)
class AdminBooking(admin.ModelAdmin):
	list_per_page = 15
	search_fields = ('user', 'check_in', 'transaction_id', 'status',)
	list_filter = ('user', 'check_in', 'transaction_id', 'status',)