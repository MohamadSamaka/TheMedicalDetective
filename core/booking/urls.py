from django.urls import path
from .views import BookingView, initBookingView



app_name = 'booking'

urlpatterns = [
    path('', BookingView.as_view(), name="index"),
]