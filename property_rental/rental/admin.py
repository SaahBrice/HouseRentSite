# rental/admin.py

from django.contrib import admin
from .models import PropertyCategory, Location, Property, Visitor, Finance, Saved, Rating, BookingReservation, SiteParameters

@admin.register(PropertyCategory)
class PropertyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('category', 'location', 'number_of_rooms', 'price_per_month', 'is_available')
    list_filter = ('category', 'location', 'is_available')
    search_fields = ('category__name', 'location__name', 'address')
    readonly_fields = ('date_available',)

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Finance)
class FinanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'number_payed_with', 'date_payed', 'motive', 'is_handled')
    list_filter = ('is_handled', 'date_payed')
    search_fields = ('user__username', 'motive')

@admin.register(Saved)
class SavedAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'property', 'date')
    list_filter = ('date',)
    search_fields = ('visitor__first_name', 'visitor__last_name', 'property__category__name')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'rating', 'comment')
    list_filter = ('rating',)
    search_fields = ('visitor__first_name', 'visitor__last_name')

@admin.register(BookingReservation)
class BookingReservationAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'date', 'is_handled', 'booking_reason')
    list_filter = ('is_handled', 'date')
    search_fields = ('visitor__first_name', 'visitor__last_name', 'booking_reason')

@admin.register(SiteParameters)
class SiteParametersAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'email', 'phone')
    fieldsets = (
        ('General Information', {
            'fields': ('site_name', 'logo', 'address', 'phone', 'email')
        }),
        ('Social Media', {
            'fields': ('twitter', 'facebook', 'instagram', 'linkedin')
        }),
        ('Legal', {
            'fields': ('privacy_policy', 'terms_and_conditions')
        }),
    )

    def has_add_permission(self, request):
        # Check if there's already an instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False