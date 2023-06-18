from .admin import my_admin_site
from core.healthcare.admin import my_doctor_site
from django.urls import path


urlpatterns = [
    path('admin/', my_admin_site.urls, name="admin-dashboard"),
    path('doctor/', my_doctor_site.urls, name="doctor-dashboard"),
]
    # path('admin/train', my_admin_site.train_model, name="train-model"),
