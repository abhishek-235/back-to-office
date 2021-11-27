from django.urls import path, re_path
from api import views
from django.conf.urls import url

urlpatterns = [
    url(r'^(?P<version>(v1))/login/', views.Login.as_view()),
    url(r'^(?P<version>(v1))/locations/', views.Location.as_view()),
    url(r'^(?P<version>(v1))/available-seats/', views.AvailableSeats.as_view()),
    url(r'^(?P<version>(v1))/booking/', views.SeatBooking.as_view()),
    
    
]