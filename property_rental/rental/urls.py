from django.urls import path
from . import views

app_name = 'rental'

urlpatterns = [
    path('', views.home, name='home'),
    path('properties/', views.property_list, name='property_list'),
    path('contact/', views.contact, name='contact'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('locations/', views.location_list, name='location_list'),
    path('visitor/register/', views.visitor_register, name='visitor_register'),
    path('visitor/login/', views.visitor_login, name='visitor_login'),
    path('visitor/logout/', views.visitor_logout, name='visitor_logout'),
    path('visitor/profile/', views.visitor_profile, name='visitor_profile'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/create/<int:property_id>/', views.booking_create, name='booking_create'),
    path('saved/', views.saved_properties, name='saved_properties'),
    path('rate/<int:property_id>/', views.rate_property, name='rate_property'),
    path('validate-access-code/<str:access_code>/', views.validate_access_code, name='validate_access_code'),
    path('submit-rating/<int:property_id>/', views.submit_rating, name='submit_rating'),
    path('submit-reservation/<int:property_id>/', views.submit_reservation, name='submit_reservation'),
]