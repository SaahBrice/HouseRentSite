from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rental.models import Property, PropertyCategory, Location, SiteParameters, Visitor, BookingReservation, Saved, Rating
from django.db.models import Count
from django.utils import timezone
from django.forms import modelform_factory
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist


from django.template.defaultfilters import register

@register.filter
def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    return ''




@login_required
def model_list(request, model_name):
    try:
        model_class = get_model_class(model_name)
        objects = model_class.objects.all()
        
        # Get field names, excluding 'id'
        field_names = [field.name for field in model_class._meta.fields if field.name != 'id']
        
        context = {
            'model_name': model_name,
            'objects': objects,
            'field_names': field_names,
        }
        return render(request, 'custom_admin/model_list.html', context)
    except Http404 as e:
        messages.error(request, str(e))
        return redirect('custom_admin:dashboard')


@login_required
def model_create(request, model_name):
    model_class = get_model_class(model_name)
    ModelForm = modelform_factory(model_class, exclude=[])
    
    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model_name.capitalize()} created successfully.')
            return redirect('custom_admin:model_list', model_name=model_name)
    else:
        form = ModelForm()
    
    context = {
        'model_name': model_name,
        'form': form,
    }
    return render(request, 'custom_admin/model_form.html', context)

@login_required
def model_update(request, model_name, pk):
    model_class = get_model_class(model_name)
    obj = get_object_or_404(model_class, pk=pk)
    ModelForm = modelform_factory(model_class, exclude=[])
    
    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{model_name.capitalize()} updated successfully.')
            return redirect('custom_admin:model_list', model_name=model_name)
    else:
        form = ModelForm(instance=obj)
    
    context = {
        'model_name': model_name,
        'form': form,
        'object': obj,
    }
    return render(request, 'custom_admin/model_form.html', context)

@login_required
def model_delete(request, model_name, pk):
    model_class = get_model_class(model_name)
    obj = get_object_or_404(model_class, pk=pk)
    
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'{model_name.capitalize()} deleted successfully.')
        return redirect('custom_admin:model_list', model_name=model_name)
    
    context = {
        'model_name': model_name,
        'object': obj,
    }
    return render(request, 'custom_admin/model_confirm_delete.html', context)


def get_model_class(model_name):
    models = {
        'property': Property,
        'category': PropertyCategory,
        'location': Location,
        'visitor': Visitor,
        'booking': BookingReservation,
        'saved': Saved,
        'rating': Rating,
        'siteparameters': SiteParameters,
    }
    model_class = models.get(model_name.lower())
    if model_class is None:
        raise Http404(f"Model '{model_name}' not found")
    return model_class



@login_required
def site_parameters(request):
    print("Site parameters view called")
    try:
        site_params = SiteParameters.objects.first()
    except ObjectDoesNotExist:
        site_params = None

    ModelForm = modelform_factory(SiteParameters, exclude=[])
    
    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES, instance=site_params)
        if form.is_valid():
            site_params = form.save()
            messages.success(request, 'Site settings updated successfully.')
            return redirect('custom_admin:site_parameters')
        else:
            print(f"Form errors: {form.errors}")  # Print form errors
    else:
        form = ModelForm(instance=site_params)
    
    context = {
        'form': form,
        'site_params': site_params,
    }
    return render(request, 'custom_admin/site_parameters.html', context)

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('custom_admin:dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')
    return render(request, 'custom_admin/login.html')

@login_required
def admin_logout(request):
    logout(request)
    return redirect('rental:home')

@login_required
def dashboard(request):
    today = timezone.now().date()
    context = {
        'total_properties': Property.objects.count(),
        'available_properties': Property.objects.filter(is_available=True).count(),
        'total_visitors': Visitor.objects.count(),
        'new_bookings': BookingReservation.objects.filter(is_handled=False).count(),
        'total_bookings': BookingReservation.objects.count(),
        'new_ratings': Rating.objects.filter(is_new=True).count(),
        'total_ratings': Rating.objects.count(),
        'recent_bookings': BookingReservation.objects.order_by('-date')[:5],
        'recent_ratings': Rating.objects.order_by('-id')[:5],
        'popular_categories': PropertyCategory.objects.annotate(property_count=Count('property')).order_by('-property_count')[:5],
        'popular_locations': Location.objects.annotate(property_count=Count('property')).order_by('-property_count')[:5],
    }
    return render(request, 'custom_admin/dashboard.html', context)