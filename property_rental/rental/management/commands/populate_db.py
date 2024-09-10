from django.core.management.base import BaseCommand
from django.utils import timezone
from rental.models import PropertyCategory, Location, Property, Visitor
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def add_arguments(self, parser):
        parser.add_argument('categories', type=int, nargs='?', default=5, help='Number of categories to create')
        parser.add_argument('locations', type=int, nargs='?', default=5, help='Number of locations to create')
        parser.add_argument('properties', type=int, nargs='?', default=20, help='Number of properties to create')
        parser.add_argument('visitors', type=int, nargs='?', default=10, help='Number of visitors to create')
        parser.add_argument('--clear', action='store_true', help='Clear the database before populating')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing database...')
            PropertyCategory.objects.all().delete()
            Location.objects.all().delete()
            Property.objects.all().delete()
            Visitor.objects.all().delete()

        self.stdout.write('Populating database...')

        # Create property categories
        categories = [
            'Appartement', 'Maison', 'Studio', 'Loft', 'Villa',
            'Duplex', 'Penthouse', 'Chalet', 'Bungalow', 'Château'
        ]
        for i in range(min(options['categories'], len(categories))):
            PropertyCategory.objects.create(name=categories[i], description=f'Description pour {categories[i]}')

        # Create locations
        locations = [
            'Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Lille',
            'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier'
        ]
        for i in range(min(options['locations'], len(locations))):
            Location.objects.create(name=locations[i], description=f'Description pour {locations[i]}')

        # Create properties
        for i in range(options['properties']):
            Property.objects.create(
                category=PropertyCategory.objects.order_by('?').first(),
                number_of_rooms=random.randint(1, 5),
                number_of_bedrooms=random.randint(1, 3),
                number_of_toilets=random.randint(1, 2),
                number_of_baths=random.randint(1, 2),
                number_of_kitchens=1,
                main_picture='properties/default.jpg',
                is_available=random.choice([True, False]),
                date_available=timezone.now() + timezone.timedelta(days=random.randint(0, 90)),
                price_per_month=random.randint(500, 2000),
                reservation_price=random.randint(100, 500),
                total_surface_area=random.randint(20, 150),
                location=Location.objects.order_by('?').first(),
                address=f'{random.randint(1, 100)} Rue Example, {random.choice(locations[:options["locations"]])}',
                caution_fees=random.randint(500, 1000),
                contract_period=random.choice([3, 6, 12]),
                description=f'Description pour la propriété {i+1}'
            )

        # Create visitors
        for i in range(options['visitors']):
            while True:
                access_code = f'{random.randint(1000, 9999)}'
                if not Visitor.objects.filter(access_code=access_code).exists():
                    Visitor.objects.create(
                        first_name=f'Prénom{i+1}',
                        last_name=f'Nom{i+1}',
                        email=f'visitor{i+1}@example.com',
                        phone_number=f'0600000000{i+1}',
                        address=f'{random.randint(1, 100)} Rue Visitor, {random.choice(locations[:options["locations"]])}',
                        sex=random.choice(['M', 'F', 'O']),
                        bio=f'Bio pour le visiteur {i+1}',
                        access_code=access_code
                    )
                    break

        self.stdout.write(self.style.SUCCESS('Database successfully populated!'))