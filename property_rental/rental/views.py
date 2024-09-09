# rental/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Property, PropertyCategory, Location, Visitor, BookingReservation, Saved, Rating
from .forms import VisitorRegistrationForm, BookingForm, RatingForm
from django.db import IntegrityError

def home(request):
    featured_properties = Property.objects.filter(is_available=True)[:3]
    return render(request, 'rental/home.html', {'featured_properties': featured_properties})

def property_list(request):
    properties = Property.objects.filter(is_available=True)
    return render(request, 'rental/property_list.html', {'properties': properties})

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'rental/property_detail.html', {'property': property})

def category_list(request):
    categories = PropertyCategory.objects.all()
    return render(request, 'rental/category_list.html', {'categories': categories})

def location_list(request):
    locations = Location.objects.all()
    return render(request, 'rental/location_list.html', {'locations': locations})

def visitor_register(request):
    if request.method == 'POST':
        form = VisitorRegistrationForm(request.POST)
        if form.is_valid():
            try:
                visitor = form.save()  # Save the visitor instance
                messages.success(request, 'Inscription réussie. Vous pouvez maintenant vous connecter avec votre code d\'accès.')
                return redirect('rental:visitor_login')
            except IntegrityError:
                # Catching the error where the access code is not unique
                form.add_error('access_code', 'Ce code d\'accès est déjà utilisé. Veuillez en choisir un autre.')
            except Exception as e:
                # For any other exceptions that might occur
                form.add_error(None, f"Une erreur est survenue: {str(e)}")
    else:
        form = VisitorRegistrationForm()
    
    return render(request, 'rental/visitor_register.html', {'form': form})

def visitor_login(request):
    if request.method == 'POST':
        access_code = request.POST.get('access_code', '').strip()  # Strip leading/trailing spaces
        
        if not access_code:
            # If the access code is empty or not provided
            messages.error(request, 'Veuillez entrer un code d\'accès valide.')
        else:
            try:
                visitor = Visitor.objects.get(access_code=access_code)
                request.session['visitor_id'] = visitor.id
                messages.success(request, 'Connexion réussie.')
                return redirect('rental:visitor_profile')
            except Visitor.DoesNotExist:
                # If the access code doesn't match any visitor
                messages.error(request, 'Code d\'accès invalide.')
    
    return render(request, 'rental/visitor_login.html')



def visitor_logout(request):
    if 'visitor_id' in request.session:
        del request.session['visitor_id']
    messages.success(request, 'Vous avez été déconnecté.')
    return redirect('rental:home')

def visitor_profile(request):
    visitor_id = request.session.get('visitor_id')
    if visitor_id:
        visitor = get_object_or_404(Visitor, pk=visitor_id)
        return render(request, 'rental/visitor_profile.html', {'visitor': visitor})
    else:
        messages.error(request, 'Veuillez vous connecter pour accéder à votre profil.')
        return redirect('rental:visitor_login')


        
def booking_list(request):
    # Assume we have some way to get the current visitor's bookings
    bookings = BookingReservation.objects.filter(visitor=request.user.visitor)
    return render(request, 'rental/booking_list.html', {'bookings': bookings})

def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.visitor = request.user.visitor
            booking.save()
            messages.success(request, 'Booking request submitted successfully.')
            return redirect('rental:booking_list')
    else:
        form = BookingForm()
    return render(request, 'rental/booking_create.html', {'form': form})

def saved_properties(request):
    saved = Saved.objects.filter(visitor=request.user.visitor)
    return render(request, 'rental/saved_properties.html', {'saved': saved})

def rate_property(request, property_id):
    property = get_object_or_404(Property, pk=property_id)
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.visitor = request.user.visitor
            rating.property = property
            rating.save()
            messages.success(request, 'Thank you for your rating.')
            return redirect('rental:property_detail', pk=property_id)
    else:
        form = RatingForm()
    return render(request, 'rental/rate_property.html', {'form': form, 'property': property})

