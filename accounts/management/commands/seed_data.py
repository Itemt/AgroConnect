import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, ProducerProfile, BuyerProfile
from inventory.models import Product, Crop
from marketplace.models import Publication

class Command(BaseCommand):
    help = 'Genera datos ficticios para la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Limpiando la base de datos...'))
        # Limpiar modelos para evitar duplicados en cada ejecución
        Publication.objects.all().delete()
        Crop.objects.all().delete()
        Product.objects.all().delete()
        ProducerProfile.objects.all().delete()
        BuyerProfile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('Iniciando la creación de datos ficticios...'))
        
        fake = Faker('es_ES')

        # --- Crear Productos Base ---
        product_names = ['Papa', 'Tomate', 'Café', 'Maíz', 'Aguacate', 'Lechuga', 'Zanahoria', 'Fresa']
        products = [Product.objects.create(name=name) for name in product_names]
        self.stdout.write(f'{len(products)} productos base creados.')

        # --- Crear 10 Productores con Cultivos y Publicaciones ---
        producer_users = []
        for i in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f'prod_{first_name.lower()}{i}'
            email = f'{username}@example.com'
            
            user = User.objects.create_user(
                username=username, email=email, password='password123',
                first_name=first_name, last_name=last_name, role='Productor'
            )
            producer_users.append(user)
            
            ProducerProfile.objects.create(
                user=user, location=fake.address(),
                farm_description=fake.text(max_nb_chars=150),
                main_crops=random.choice(product_names)
            )
            self.stdout.write(f'Productor creado: {username}')

            # Crear 1 a 3 cultivos por productor
            for _ in range(random.randint(1, 3)):
                crop_status = random.choice(['listo para cosechar', 'cosechado'])
                estimated_quantity = random.randint(50, 500)
                
                crop = Crop.objects.create(
                    product=random.choice(products),
                    producer=user,
                    estimated_quantity=estimated_quantity,
                    unit='kg',
                    status=crop_status,
                    estimated_availability_date=timezone.now().date() + timedelta(days=random.randint(-10, 10))
                )

                # Crear una publicación para los cultivos listos
                if crop_status in ['listo para cosechar', 'cosechado']:
                    Publication.objects.create(
                        crop=crop,
                        price_per_unit=round(random.uniform(0.5, 5.0), 2),
                        available_quantity=estimated_quantity - random.randint(0, 20),
                        status='disponible'
                    )
                    self.stdout.write(f'  -> Publicación creada para el cultivo de {crop.product.name}')

        # --- Crear 10 Compradores ---
        for i in range(10):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f'comp_{first_name.lower()}{i}'
            email = f'{username}@example.com'
            
            user = User.objects.create_user(
                username=username, email=email, password='password123',
                first_name=first_name, last_name=last_name, role='Comprador'
            )
            
            BuyerProfile.objects.create(
                user=user, company_name=fake.company(),
                business_type=random.choice(['Restaurante', 'Supermercado', 'Distribuidor', 'Tienda Local'])
            )
            self.stdout.write(f'Comprador creado: {username}')

        self.stdout.write(self.style.SUCCESS('¡Datos ficticios creados exitosamente!'))
