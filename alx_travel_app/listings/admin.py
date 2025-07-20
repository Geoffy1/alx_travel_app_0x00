# alx_travel_app/listings/admin.py
from django.contrib import admin
from .models import Listing, Booking, Review

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'price_per_night', 'owner', 'city', 'country', 'created_at')
    list_filter = ('city', 'country', 'num_bedrooms', 'max_guests')
    search_fields = ('title', 'description', 'address', 'owner__username')
    raw_id_fields = ('owner',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('listing', 'guest', 'check_in_date', 'check_out_date', 'total_price', 'status')
    list_filter = ('status', 'check_in_date', 'check_out_date')
    search_fields = ('listing__title', 'guest__username')
    raw_id_fields = ('listing', 'guest')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('listing', 'guest', 'rating', 'comment', 'created_at')
    list_filter = ('rating',)
    search_fields = ('listing__title', 'guest__username', 'comment')
    raw_id_fields = ('listing', 'guest')
