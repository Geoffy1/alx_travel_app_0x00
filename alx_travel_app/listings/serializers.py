from rest_framework import serializers
from .models import Listing, Booking, Review
from django.contrib.auth import get_user_model


User = get_user_model()

# Although not required for Milestone 2, ReviewSerializer included
# because ListingSerializer uses it for nested representation.
class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    """
    guest_username = serializers.ReadOnlyField(source='guest.username')

    class Meta:
        model = Review
        fields = ['id', 'listing', 'guest', 'guest_username', 'rating', 'comment', 'created_at']
        read_only_fields = ['guest', 'created_at', 'updated_at']

class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Listing model.
    Includes nested serializers for related data like reviews.
    """
    reviews = ReviewSerializer(many=True, read_only=True)
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price_per_night', 'num_bedrooms',
            'num_bathrooms', 'max_guests', 'address', 'city', 'country',
            'latitude', 'longitude', 'owner', 'owner_username',
            'created_at', 'updated_at', 'reviews'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    """
    listing_title = serializers.ReadOnlyField(source='listing.title')
    guest_username = serializers.ReadOnlyField(source='guest.username')

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'guest', 'guest_username',
            'check_in_date', 'check_out_date', 'total_price', 'num_guests',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['guest', 'status', 'created_at', 'updated_at']
