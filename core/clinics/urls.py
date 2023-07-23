from django.urls import path
from . import views

urlpatterns = [
    path('clinics', views.index, name="clinics"),
]
