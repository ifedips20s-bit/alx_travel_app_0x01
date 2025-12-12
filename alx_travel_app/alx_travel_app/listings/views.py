import requests
from django.conf import settings
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Listing, Payment
from .serializers import ListingSerializer
from bookings.models import Booking
from bookings.serializers import BookingSerializer

# --- ViewSets ---
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

# --- Payment API Views ---
@api_view(['POST'])
def initiate_payment(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    amount = booking.total_price
    tx_ref = f"BOOK-{booking.id}-{booking.user.id}"

    payload = {
        "amount": float(amount),
        "currency": "ETB",
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "tx_ref": tx_ref,
        "callback_url": request.build_absolute_uri("/payments/verify/")
    }

    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if data["status"] == "success":
        Payment.objects.create(
            user=request.user,
            booking=booking,
            amount=amount,
            transaction_id=tx_ref,
            status='pending'
        )
        return redirect(data["data"]["checkout_url"])
    return Response({"error": "Payment initiation failed"}, status=400)

@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.GET.get("tx_ref")
    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
    except Payment.DoesNotExist:
        return Response({"error": "Invalid transaction"}, status=404)

    headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
    response = requests.get(f"https://api.chapa.co/v1/transaction/verify/{tx_ref}", headers=headers)
    data = response.json()

    if data["status"] == "success" and data["data"]["status"] == "success":
        payment.status = "completed"
        payment.save()
        # send confirmation email via Celery
        from .tasks import send_payment_confirmation_email
        send_payment_confirmation_email.delay(payment.id)
        return redirect("/payment/success/")
    else:
        payment.status = "failed"
        payment.save()
        return redirect("/payment/failed/")
