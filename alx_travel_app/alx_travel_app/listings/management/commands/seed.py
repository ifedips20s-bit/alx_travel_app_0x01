from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from faker import Faker
import random

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews'

    def handle(self, *args, **kwargs):
        # Create Users
        for _ in range(5):
            User.objects.create_user(username=fake.user_name(), password='password123')

        users = User.objects.all()

        # Create Listings
        for _ in range(10):
            Listing.objects.create(
                name=fake.company(),
                description=fake.text(),
                price_per_night=random.randint(50, 500),
                location=fake.city(),
                host=random.choice(users)
            )

        listings = Listing.objects.all()

        # Create Bookings
        for _ in range(20):
            Booking.objects.create(
                listing=random.choice(listings),
                user=random.choice(users),
                check_in=fake.date_between(start_date='today', end_date='+30d'),
                check_out=fake.date_between(start_date='+31d', end_date='+60d')
            )

        # Create Reviews
        for _ in range(30):
            Review.objects.create(
                listing=random.choice(listings),
                user=random.choice(users),
                rating=random.randint(1, 5),
                comment=fake.text()
            )

        self.stdout.write(self.style.SUCCESS('Database successfully seeded!'))
