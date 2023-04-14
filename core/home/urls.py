from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('<int:id>/', views.test, name="test"),
    # path('home', views.index, name="home")
    # path('/home', views.index, name="home"),
]
