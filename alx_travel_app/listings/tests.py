# alx_travel_app/listings/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer # ReviewSerializer included for ListingSerializer's nested reviews

User = get_user_model()

class ListingModelTest(TestCase):
    """Tests for the Listing model."""
    def setUp(self):
        self.owner_user = User.objects.create_user(username='owner1', email='owner1@example.com', password='testpassword')
        self.listing = Listing.objects.create(
            title='Cozy Test Cabin',
            description='A small cabin for testing.',
            price_per_night=100.00,
            num_bedrooms=1,
            num_bathrooms=1,
            max_guests=2,
            address='123 Test Rd',
            city='Testville',
            country='Testland',
            latitude=10.0,
            longitude=20.0,
            owner=self.owner_user,
        )

    def test_listing_creation(self):
        self.assertEqual(self.listing.title, 'Cozy Test Cabin')
        self.assertEqual(float(self.listing.price_per_night), 100.00)
        self.assertTrue(isinstance(self.listing, Listing))
        self.assertIsNotNone(self.listing.created_at)
        self.assertEqual(self.listing.owner, self.owner_user)

    def test_listing_str_method(self):
        self.assertEqual(str(self.listing), 'Cozy Test Cabin')

    def test_price_per_night_validation(self):
        with self.assertRaises(ValidationError):
            invalid_listing = Listing(
                title='Invalid Price Listing',
                description='Should fail due to invalid price.',
                price_per_night=-5.00,
                num_bedrooms=1, num_bathrooms=1, max_guests=1,
                address='X', city='Y', country='Z', owner=self.owner_user
            )
            invalid_listing.full_clean()

    def test_num_bedrooms_validation(self):
        with self.assertRaises(ValidationError):
            invalid_listing = Listing(
                title='Invalid Bed Listing',
                description='Should fail due to invalid bedrooms.',
                price_per_night=10.00,
                num_bedrooms=0,
                num_bathrooms=1, max_guests=1,
                address='X', city='Y', country='Z', owner=self.owner_user
            )
            invalid_listing.full_clean()

class BookingModelTest(TestCase):
    """Tests for the Booking model."""
    def setUp(self):
        self.guest_user = User.objects.create_user(username='guestuser', email='guest@example.com', password='guestpassword')
        self.owner_user = User.objects.create_user(username='owner_b', email='ownerb@example.com', password='password')
        self.listing = Listing.objects.create(
            title='Booking Test Spot',
            description='Place for booking tests.',
            price_per_night=50.00,
            num_bedrooms=1, num_bathrooms=1, max_guests=2,
            address='456 Booking St', city='Booktown', country='Bookland',
            owner=self.owner_user
        )
        self.check_in = date.today() + timedelta(days=10)
        self.check_out = self.check_in + timedelta(days=5)
        self.booking = Booking.objects.create(
            listing=self.listing,
            guest=self.guest_user,
            check_in_date=self.check_in,
            check_out_date=self.check_out,
            total_price=250.00,
            num_guests=1,
            status='PENDING'
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.guest, self.guest_user)
        self.assertEqual(self.booking.listing, self.listing)
        self.assertEqual(self.booking.status, 'PENDING')
        self.assertEqual(self.booking.num_guests, 1)
        self.assertEqual(float(self.booking.total_price), 250.00)

    def test_booking_str_method(self):
        expected_str = f"Booking for {self.listing.title} by {self.guest_user.username} from {self.check_in} to {self.check_out}"
        self.assertEqual(str(self.booking), expected_str)

    def test_booking_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                listing=self.listing,
                guest=self.guest_user,
                check_in_date=self.check_in,
                check_out_date=self.check_out,
                total_price=100.00,
                num_guests=1,
                status='CONFIRMED'
            )

    def test_booking_status_choices(self):
        self.booking.status = 'INVALID_STATUS'
        with self.assertRaises(ValidationError):
            self.booking.full_clean()

class ReviewModelTest(TestCase):
    """Tests for the Review model."""
    def setUp(self):
        self.reviewer_user = User.objects.create_user(username='reviewer', email='reviewer@example.com', password='reviewpass')
        self.owner_user = User.objects.create_user(username='owner_r', email='ownerr@example.com', password='password')
        self.listing = Listing.objects.create(
            title='Review Test Place',
            description='For review tests.',
            price_per_night=80.00,
            num_bedrooms=1, num_bathrooms=1, max_guests=2,
            address='789 Review Lane', city='Reviewville', country='Reviewland',
            owner=self.owner_user
        )
        self.review = Review.objects.create(
            listing=self.listing,
            guest=self.reviewer_user,
            rating=4,
            comment='Very good experience!'
        )

    def test_review_creation(self):
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, 'Very good experience!')
        self.assertEqual(self.review.guest, self.reviewer_user)
        self.assertEqual(self.review.listing, self.listing)

    def test_review_str_method(self):
        expected_str = f"Review for {self.listing.title} by {self.reviewer_user.username} - Rating: {self.review.rating}"
        self.assertEqual(str(self.review), expected_str)

    def test_rating_validation(self):
        with self.assertRaises(ValidationError):
            invalid_review_low = Review(
                listing=self.listing, guest=self.reviewer_user, rating=0, comment='Too low'
            )
            invalid_review_low.full_clean()

        with self.assertRaises(ValidationError):
            invalid_review_high = Review(
                listing=self.listing, guest=self.reviewer_user, rating=6, comment='Too high'
            )
            invalid_review_high.full_clean()

    def test_unique_review_per_guest_per_listing(self):
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                listing=self.listing,
                guest=self.reviewer_user,
                rating=5,
                comment='Second review, should fail'
            )

class ListingSerializerTest(TestCase):
    """Tests for the ListingSerializer."""
    def setUp(self):
        self.owner_user = User.objects.create_user(username='owner_serializer', email='owner_s@example.com', password='password')
        self.guest_user = User.objects.create_user(username='guest_serializer', email='guest_s@example.com', password='password')
        self.listing = Listing.objects.create(
            title='Serializer Test House',
            description='Sunny and fun for serializer tests',
            price_per_night=250.00,
            num_bedrooms=2,
            num_bathrooms=1,
            max_guests=4,
            address='Ocean Front Drive',
            city='Malibu',
            country='USA',
            latitude=34.0,
            longitude=-118.0,
            owner=self.owner_user
        )
        self.review1 = Review.objects.create(listing=self.listing, guest=self.guest_user, rating=5, comment='Amazing!')
        self.review2 = Review.objects.create(listing=self.listing, guest=self.owner_user, rating=4, comment='Very good.')


    def test_listing_serializer_fields(self):
        serializer = ListingSerializer(instance=self.listing)
        data = serializer.data

        expected_fields = {
            'id', 'title', 'description', 'price_per_night', 'num_bedrooms',
            'num_bathrooms', 'max_guests', 'address', 'city', 'country',
            'latitude', 'longitude', 'owner', 'owner_username',
            'created_at', 'updated_at', 'reviews'
        }
        self.assertEqual(set(data.keys()), expected_fields)

        self.assertEqual(data['title'], 'Serializer Test House')
        self.assertEqual(float(data['price_per_night']), 250.00)
        self.assertEqual(data['owner_username'], 'owner_serializer')
        self.assertEqual(len(data['reviews']), 2)
        self.assertEqual(data['reviews'][0]['rating'], 5)
        self.assertEqual(data['reviews'][0]['guest_username'], 'guest_serializer')


    def test_listing_serializer_read_only_fields(self):
        original_owner = self.listing.owner
        data = {'title': 'New Title', 'created_at': '2020-01-01T00:00:00Z', 'owner': 999}
        serializer = ListingSerializer(instance=self.listing, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.listing.refresh_from_db()
        self.assertNotEqual(str(self.listing.created_at.year), '2020')
        self.assertEqual(self.listing.owner, original_owner)
        self.assertEqual(self.listing.title, 'New Title')

class BookingSerializerTest(TestCase):
    """Tests for the BookingSerializer."""
    def setUp(self):
        self.guest_user = User.objects.create_user(username='guest_booking_s', email='guest_booking_s@example.com', password='pass')
        self.owner_user = User.objects.create_user(username='owner_booking_s', email='owner_booking_s@example.com', password='pass')
        self.listing = Listing.objects.create(
            title='Bookable Serializer Spot',
            description='For booking serializer tests.',
            price_per_night=100.00,
            num_bedrooms=1, num_bathrooms=1, max_guests=2,
            address='Booking Serializer St', city='SerializerVille', country='USA',
            owner=self.owner_user
        )
        self.check_in = date.today() + timedelta(days=15)
        self.check_out = self.check_in + timedelta(days=3)
        self.booking = Booking.objects.create(
            listing=self.listing,
            guest=self.guest_user,
            check_in_date=self.check_in,
            check_out_date=self.check_out,
            total_price=300.00,
            num_guests=2,
            status='PENDING'
        )

    def test_booking_serializer_fields(self):
        serializer = BookingSerializer(instance=self.booking)
        data = serializer.data

        expected_fields = {
            'id', 'listing', 'listing_title', 'guest', 'guest_username',
            'check_in_date', 'check_out_date', 'total_price', 'num_guests',
            'status', 'created_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

        self.assertEqual(data['listing_title'], 'Bookable Serializer Spot')
        self.assertEqual(data['guest_username'], 'guest_booking_s')
        self.assertEqual(float(data['total_price']), 300.00)
        self.assertEqual(data['status'], 'PENDING')
        self.assertEqual(data['check_in_date'], str(self.check_in))

    def test_booking_serializer_read_only_fields(self):
        original_status = self.booking.status
        original_guest = self.booking.guest
        data = {'status': 'CONFIRMED', 'guest': self.guest_user.id + 1}
        serializer = BookingSerializer(instance=self.booking, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, original_status)
        self.assertEqual(self.booking.guest, original_guest)
