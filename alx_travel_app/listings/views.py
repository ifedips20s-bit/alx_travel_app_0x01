from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Listings
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Bookings
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

