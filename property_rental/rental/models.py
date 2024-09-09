from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
User = get_user_model()

class PropertyCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(verbose_name="Description", blank=True)

    class Meta:
        verbose_name = "Catégorie de propriété"
        verbose_name_plural = "Catégories de propriétés"

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(verbose_name="Description", blank=True)

    class Meta:
        verbose_name = "Emplacement"
        verbose_name_plural = "Emplacements"

    def __str__(self):
        return self.name

class Property(models.Model):
    CONTRACT_CHOICES = [
        (3, '3 mois'),
        (6, '6 mois'),
        (12, '1 an'),
    ]

    category = models.ForeignKey(PropertyCategory, on_delete=models.PROTECT, verbose_name="Catégorie")
    number_of_rooms = models.PositiveIntegerField(verbose_name="Nombre de pièces", default=1)
    number_of_bedrooms = models.PositiveIntegerField(verbose_name="Nombre de chambres", default=1)
    number_of_toilets = models.PositiveIntegerField(verbose_name="Nombre de toilettes", default=1)
    number_of_baths = models.PositiveIntegerField(verbose_name="Nombre de salles de bain", default=1)
    number_of_kitchens = models.PositiveIntegerField(verbose_name="Nombre de cuisines", default=1)
    main_picture = models.ImageField(upload_to='properties/', verbose_name="Image principale")
    picture_1 = models.ImageField(upload_to='properties/', blank=True, null=True, verbose_name="Image 1")
    picture_2 = models.ImageField(upload_to='properties/', blank=True, null=True, verbose_name="Image 2")
    picture_3 = models.ImageField(upload_to='properties/', blank=True, null=True, verbose_name="Image 3")
    picture_4 = models.ImageField(upload_to='properties/', blank=True, null=True, verbose_name="Image 4")
    picture_5 = models.ImageField(upload_to='properties/', blank=True, null=True, verbose_name="Image 5")
    is_available = models.BooleanField(default=True, verbose_name="Disponible")
    date_available = models.DateField(verbose_name="Date de disponibilité", default=timezone.now)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix par mois")
    reservation_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de réservation")
    total_surface_area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Surface totale (m²)")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, verbose_name="Emplacement")
    address = models.TextField(verbose_name="Adresse")
    caution_fees = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Frais de caution")
    contract_period = models.IntegerField(choices=CONTRACT_CHOICES, verbose_name="Période de contrat", default=12)
    description = models.TextField(verbose_name="Description", blank=True)

    class Meta:
        verbose_name = "Propriété"
        verbose_name_plural = "Propriétés"

    def __str__(self):
        return f"{self.category} à {self.location}"

class Visitor(models.Model):
    SEX_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    ]

    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(verbose_name="Email")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    address = models.TextField(verbose_name="Adresse")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name="Sexe")
    bio = models.TextField(blank=True, verbose_name="Biographie")
    access_code = models.CharField(max_length=20, unique=True, verbose_name="Code d'accès")

    class Meta:
        verbose_name = "Visiteur"
        verbose_name_plural = "Visiteurs"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        if len(self.access_code) != 4:
            raise ValidationError("Le code d'accès doit contenir exactement 4 caractères.")
        if not self.access_code.isalnum():
            raise ValidationError("Le code d'accès doit contenir uniquement des lettres et des chiffres.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Finance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    number_payed_with = models.CharField(max_length=100, verbose_name="Numéro de paiement")
    date_payed = models.DateTimeField(auto_now_add=True, verbose_name="Date de paiement")
    motive = models.CharField(max_length=255, verbose_name="Motif")
    is_handled = models.BooleanField(default=False, verbose_name="Traité")

    class Meta:
        verbose_name = "Finance"
        verbose_name_plural = "Finances"

    def __str__(self):
        return f"Paiement de {self.user} le {self.date_payed}"

class Saved(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, verbose_name="Propriété")
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, verbose_name="Visiteur")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'enregistrement")

    class Meta:
        verbose_name = "Sauvegarde"
        verbose_name_plural = "Sauvegardes"

    def __str__(self):
        return f"{self.visitor} a sauvegardé {self.property}"

class Rating(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, verbose_name="Visiteur")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Note", default=2)
    comment = models.TextField(verbose_name="Commentaire", blank=True)

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"

    def __str__(self):
        return f"Évaluation de {self.visitor}"

class BookingReservation(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, verbose_name="Visiteur")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date de réservation")
    is_handled = models.BooleanField(default=False, verbose_name="Traitée")
    booking_reason = models.TextField(verbose_name="Raison de la réservation", blank=True)

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"

    def __str__(self):
        return f"Réservation de {self.visitor} le {self.date}"

class SiteParameters(models.Model):
    address = models.TextField(verbose_name="Adresse")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(verbose_name="Email", default="contact@example.com")
    twitter = models.URLField(blank=True, verbose_name="Twitter")
    facebook = models.URLField(blank=True, verbose_name="Facebook")
    instagram = models.URLField(blank=True, verbose_name="Instagram")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    privacy_policy = models.TextField(verbose_name="Politique de confidentialité")
    terms_and_conditions = models.TextField(verbose_name="Conditions d'utilisation")
    logo = models.ImageField(upload_to='site/', verbose_name="Logo", blank=True, null=True)
    site_name = models.CharField(max_length=100, verbose_name="Nom du site", default="Gestion de Location")

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"

    def __str__(self):
        return self.site_name
