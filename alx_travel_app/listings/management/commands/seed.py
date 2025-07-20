# alx_travel_app/listings/management/commands/seed.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from listings.models import Listing, Booking, Review
from django.utils import timezone
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with sample listings, bookings, and reviews.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Clear existing data (optional, but good for repeatable seeding)
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleaned existing Listing, Booking, and Review data.'))

        # --- User Creation (if not already existing) ---
        try:
            admin_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
            self.stdout.write(self.style.SUCCESS(f"Created superuser: {admin_user.username}"))

        try:
            host_user = User.objects.get(username='host')
        except User.DoesNotExist:
            host_user = User.objects.create_user('host', 'host@example.com', 'hostpassword')
            self.stdout.write(self.style.SUCCESS(f"Created host user: {host_user.username}"))

        try:
            guest_user = User.objects.get(username='guest')
        except User.DoesNotExist:
            guest_user = User.objects.create_user('guest', 'guest@example.com', 'guestpassword')
            self.stdout.write(self.style.SUCCESS(f"Created guest user: {guest_user.username}"))

        users_for_bookings_reviews = [guest_user, admin_user]

        # --- Listing Seeding ---
        self.stdout.write(self.style.SUCCESS('Seeding listings...'))
        sample_listings_data = [
            {
                'title': 'Cozy Downtown Apartment',
                'description': 'A charming and comfortable apartment in the heart of the city, perfect for couples.',
                'price_per_night': 120.00,
                'num_bedrooms': 1,
                'num_bathrooms': 1,
                'max_guests': 2,
                'address': '123 Main St',
                'city': 'New York',
                'country': 'USA',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'owner': host_user,
            },
            {
                'title': 'Spacious Family Villa with Pool',
                'description': 'Beautiful villa with a private pool and garden, ideal for family vacations.',
                'price_per_night': 350.00,
                'num_bedrooms': 4,
                'num_bathrooms': 3,
                'max_guests': 8,
                'address': '456 Ocean Ave',
                'city': 'Miami',
                'country': 'USA',
                'latitude': 25.7617,
                'longitude': -80.1918,
                'owner': host_user,
            },
            {
                'title': 'Secluded Mountain Cabin',
                'description': 'Escape to nature in this peaceful cabin. Great for hiking and relaxation.',
                'price_per_night': 90.00,
                'num_bedrooms': 2,
                'num_bathrooms': 1,
                'max_guests': 4,
                'address': '789 Forest Rd',
                'city': 'Asheville',
                'country': 'USA',
                'latitude': 35.6009,
                'longitude': -82.5540,
                'owner': host_user,
            },
        ]

        listings = []
        for data in sample_listings_data:
            listing = Listing.objects.create(**data)
            listings.append(listing)
            self.stdout.write(self.style.SUCCESS(f"Created listing: {listing.title}"))

        # --- Booking Seeding ---
        self.stdout.write(self.style.SUCCESS('Seeding bookings...'))
        for _ in range(len(listings) * 2):
            listing = random.choice(listings)
            guest = random.choice(users_for_bookings_reviews)

            check_in_date = timezone.now().date() + timedelta(days=random.randint(1, 60))
            check_out_date = check_in_date + timedelta(days=random.randint(2, 10))
            num_guests = random.randint(1, listing.max_guests)
            total_price = listing.price_per_night * (check_out_date - check_in_date).days

            try:
                booking = Booking.objects.create(
                    listing=listing,
                    guest=guest,
                    check_in_date=check_in_date,
                    check_out_date=check_out_date,
                    total_price=total_price,
                    num_guests=num_guests,
                    status=random.choice([choice[0] for choice in Booking.STATUS_CHOICES])
                )
                self.stdout.write(self.style.SUCCESS(f"Created booking for {listing.title} by {guest.username}"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not create booking for {listing.title} ({e})"))


        # --- Review Seeding ---
        self.stdout.write(self.style.SUCCESS('Seeding reviews...'))
        for listing in listings:
            num_reviews_for_listing = random.randint(1, 2)
            for _ in range(num_reviews_for_listing):
                guest = random.choice(users_for_bookings_reviews)
                rating = random.randint(1, 5)
                comment = random.choice([
                    "Absolutely loved my stay! Highly recommend.",
                    "Great place, very clean and comfortable. Will book again.",
                    "The host was very responsive and helpful throughout our stay.",
                    "Good location, but could use some modern updates.",
                    "Fantastic experience, everything was as described and more!",
                ])

                try:
                    review = Review.objects.create(
                        listing=listing,
                        guest=guest,
                        rating=rating,
                        comment=comment
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created review for {listing.title} by {guest.username} (Rating: {rating})"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Could not create review for {listing.title} by {guest.username} ({e})"))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
