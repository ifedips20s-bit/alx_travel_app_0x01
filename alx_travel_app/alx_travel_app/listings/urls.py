from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, initiate_payment, verify_payment

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('payment/initiate/<int:booking_id>/', initiate_payment, name='initiate-payment'),
    path('payment/verify/', verify_payment, name='verify-payment'),
    path('', include(router.urls)),
]
