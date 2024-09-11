# rental/views.py

import json
import math
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Property, PropertyCategory, Location, Visitor, BookingReservation, Saved, Rating
from .forms import VisitorRegistrationForm, BookingForm, RatingForm
from django.db.models import Avg




def home(request):
    available_properties = Property.objects.filter(is_available=True)[:6]
    soon_available_properties = Property.objects.filter(is_available=False)[:6]
    all_properties = Property.objects.all()[:6]
    categories = PropertyCategory.objects.all()
    locations = Location.objects.all()
    context = {
        'available_properties': available_properties,
        'soon_available_properties': soon_available_properties,
        'all_properties': all_properties,
        'categories': categories,
        'locations': locations,
    }
    return render(request, 'rental/index.html', context)



def property_list(request):
    # Get filter values from the GET request (with default values set to 'all')
    selected_category_id = request.GET.get('category', 'all')
    selected_location_id = request.GET.get('location', 'all')

    # Base query for available properties
    available_properties = Property.objects.filter(is_available=True)
    soon_available_properties = Property.objects.filter(is_available=False)

    # Apply category filter if selected
    if selected_category_id != 'all':
        available_properties = available_properties.filter(category_id=selected_category_id)
        soon_available_properties = soon_available_properties.filter(category_id=selected_category_id)

    # Apply location filter if selected
    if selected_location_id != 'all':
        available_properties = available_properties.filter(location_id=selected_location_id)
        soon_available_properties = soon_available_properties.filter(location_id=selected_location_id)

    # Check if either of the queries is empty
    available_empty = not available_properties.exists()
    soon_available_empty = not soon_available_properties.exists()

    # Context for the template
    categories = PropertyCategory.objects.all()
    locations = Location.objects.all()

    context = {
        'available_properties': available_properties,
        'soon_available_properties': soon_available_properties,
        'categories': categories,
        'locations': locations,
        'selected_category_id': selected_category_id,
        'selected_location_id': selected_location_id,
        'available_empty': available_empty,
        'soon_available_empty': soon_available_empty,
    }
    
    return render(request, 'rental/property_list.html', context)



def contact(request):
    return render(request, 'rental/contact.html')


def submit_rating(request, property_id):
    if request.method == 'POST':
        try:
            # Fetch the visitor_id from session
            visitor_id = request.session.get('visitor_id')
            if not visitor_id:
                return JsonResponse({'success': False, 'error': 'Utilisateur non connecté.'}, status=401)

            # Try to fetch the visitor and property
            visitor = Visitor.objects.get(id=visitor_id)
            property = Property.objects.get(id=property_id)

            # Parse the incoming JSON data
            data = json.loads(request.body)
            rating_value = data.get('rating')
            comment = data.get('comment', '')

            # Validate rating
            if rating_value is None or not (1 <= int(rating_value) <= 5):
                return JsonResponse({'success': False, 'error': 'Note invalide.'}, status=400)

            # Create and save the rating
            Rating.objects.create(
                visitor=visitor,
                property_rated=property,
                rating=rating_value,
                comment=comment
            )

            return JsonResponse({'success': True, 'message': 'Votre note a été soumise.'})

        except Visitor.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Visiteur non trouvé.'}, status=404)
        except Property.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Propriété non trouvée.'}, status=404)
        except Exception as e:
            # Catch any other errors and log them
            print(f"Error occurred: {str(e)}")  # This will log the actual error in the terminal
            return JsonResponse({'success': False, 'error': f'Une erreur est survenue: {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)




def submit_reservation(request, property_id):
    if request.method == 'POST':
        try:
            # Fetch the visitor_id from session
            visitor_id = request.session.get('visitor_id')
            if not visitor_id:
                return JsonResponse({'success': False, 'error': 'Utilisateur non connecté.'}, status=401)

            visitor = Visitor.objects.get(id=visitor_id)
            property = Property.objects.get(id=property_id)

            # Parse the incoming JSON data
            data = json.loads(request.body)
            reservation_reason = data.get('reason', '')

            # Validate input (add further validation as needed)
            if not reservation_reason:
                return JsonResponse({'success': False, 'error': 'Veuillez indiquer la raison de votre réservation.'}, status=400)

            # Create and save the reservation
            BookingReservation.objects.create(
                visitor=visitor,
                property=property,
                booking_reason=reservation_reason
            )

            return JsonResponse({'success': True, 'message': 'Votre réservation a été soumise.'})

        except Visitor.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Visiteur non trouvé.'}, status=404)
        except Property.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Propriété non trouvée.'}, status=404)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({'success': False, 'error': f'Une erreur est survenue: {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)





def validate_access_code(request, access_code):
    try:
        # Check if visitor exists with the provided access code
        visitor = Visitor.objects.get(access_code=access_code)
        
        # Log the visitor in by saving their ID in the session
        request.session['visitor_id'] = visitor.id  # Automatically log the visitor in

        # Return a successful JSON response with visitor name
        return JsonResponse({'visitor_exists': True, 'visitor_name': visitor.first_name})

    except Visitor.DoesNotExist:
        # If no visitor is found, return JSON response indicating the visitor does not exist
        return JsonResponse({'visitor_exists': False})

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    additional_pictures = [
        property.picture_1,
        property.picture_2,
        property.picture_3,
        property.picture_4,
        property.picture_5
    ]
        # Calculate the average rating for the property
    average_rating = Rating.objects.filter(property_rated=property).aggregate(Avg('rating'))['rating__avg']
    
    # Handle case when there are no ratings
    if average_rating is None:
        average_rating = 0  # No ratings yet
    stars_range = range(1, 6)
    print(average_rating)
    print(stars_range)
    # Round the average rating to the nearest whole number
    average_rating = math.ceil(average_rating)
    top_ratings = Rating.objects.filter(property_rated=property).order_by('-rating', '-id')[:3]
    print(top_ratings)
    context = {
        'property': property,
        'additional_pictures': additional_pictures,
        'average_rating': average_rating,
        'stars_range': stars_range,
        'top_ratings': top_ratings,
    }
    return render(request, 'rental/property_detail.html', context)

def category_list(request):
    categories = PropertyCategory.objects.all()
    return render(request, 'rental/category_list.html', {'categories': categories})

def location_list(request):
    locations = Location.objects.all()
    return render(request, 'rental/location_list.html', {'locations': locations})

def visitor_register(request):
    if request.method == 'POST':
        try:
            # Parse JSON request body
            data = json.loads(request.body)
            
            # Create form instance using the submitted data
            form = VisitorRegistrationForm(data)
            
            if form.is_valid():
                # Save the visitor
                visitor = form.save()
                # Log the visitor in by saving their ID in the session
                request.session['visitor_id'] = visitor.id
                
                return JsonResponse({'success': True, 'message': 'Inscription réussie. Vous pouvez maintenant réserver.'})
            else:
                # Return form validation errors
                return JsonResponse({'success': False, 'error': form.errors.as_json()}, status=400)
        
        except Exception as e:
            # Catch any other errors
            return JsonResponse({'success': False, 'error': f'Une erreur est survenue: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée.'}, status=405)

def visitor_login(request):
    if request.method == 'POST':
        access_code = request.POST.get('access_code', '').strip()  # Strip leading/trailing spaces
        
        if not access_code:
            messages.error(request, 'Veuillez entrer un code d\'accès valide.')
        else:
            try:
                visitor = Visitor.objects.get(access_code=access_code)
                request.session['visitor_id'] = visitor.id  # Store visitor ID in session
                messages.success(request, 'Connexion réussie.')
                return redirect('rental:visitor_profile')  # Redirect to profile or appropriate page
            except Visitor.DoesNotExist:
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
    visitor_id = request.session.get('visitor_id')
    if visitor_id:
        visitor = get_object_or_404(Visitor, pk=visitor_id)
        bookings = BookingReservation.objects.filter(visitor=visitor)
        return render(request, 'rental/booking_list.html', {'bookings': bookings})
    else:
        messages.error(request, 'Veuillez vous connecter pour voir vos réservations.')
        return redirect('rental:visitor_login')



def booking_create(request, property_id):
    visitor_id = request.session.get('visitor_id')
    if visitor_id:
        visitor = get_object_or_404(Visitor, pk=visitor_id)
        property = get_object_or_404(Property, pk=property_id)
        if request.method == 'POST':
            form = BookingForm(request.POST)
            if form.is_valid():
                booking = form.save(commit=False)
                booking.visitor = visitor
                booking.property = property
                booking.save()
                messages.success(request, 'Demande de réservation soumise avec succès.')
                return redirect('rental:booking_list')
        else:
            form = BookingForm()
        return render(request, 'rental/booking_create.html', {'form': form, 'property': property})
    else:
        messages.error(request, 'Veuillez vous connecter pour faire une réservation.')
        return redirect('rental:visitor_login')


def saved_properties(request):
    visitor_id = request.session.get('visitor_id')
    if visitor_id:
        visitor = get_object_or_404(Visitor, pk=visitor_id)
        saved = Saved.objects.filter(visitor=visitor)
        return render(request, 'rental/saved_properties.html', {'saved': saved})
    else:
        messages.error(request, 'Veuillez vous connecter pour voir vos propriétés sauvegardées.')
        return redirect('rental:visitor_login')



def rate_property(request, property_id):
    visitor_id = request.session.get('visitor_id')
    if visitor_id:
        visitor = get_object_or_404(Visitor, pk=visitor_id)
        property = get_object_or_404(Property, pk=property_id)
        if request.method == 'POST':
            form = RatingForm(request.POST)
            if form.is_valid():
                rating = form.save(commit=False)
                rating.visitor = visitor
                rating.property = property
                rating.save()
                messages.success(request, 'Merci pour votre évaluation.')
                return redirect('rental:property_detail', pk=property_id)
        else:
            form = RatingForm()
        return render(request, 'rental/rate_property.html', {'form': form, 'property': property})
    else:
        messages.error(request, 'Veuillez vous connecter pour évaluer une propriété.')
        return redirect('rental:visitor_login')