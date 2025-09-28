import random
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, ProducerProfile, BuyerProfile
from inventory.models import Product, Crop
from marketplace.models import Publication
from core.colombia_locations import COLOMBIA_LOCATIONS

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
        productos_por_categoria = {
            'hortalizas': [
                'Papa', 'Tomate', 'Lechuga', 'Zanahoria', 'Cebolla', 'Pimiento', 'Pepino', 'Brócoli',
                'Coliflor', 'Repollo', 'Espinaca', 'Rábano', 'Apio', 'Berenjena', 'Calabacín', 'Calabaza',
                'Remolacha', 'Nabo', 'Puerro', 'Ajo', 'Acelga', 'Cilantro', 'Perejil'
            ],
            'frutas': [
                'Aguacate', 'Fresa', 'Manzana', 'Pera', 'Durazno', 'Ciruela', 'Uva', 'Naranja',
                'Limón', 'Mandarina', 'Toronja', 'Mango', 'Papaya', 'Piña', 'Banano', 'Plátano',
                'Sandía', 'Melón', 'Kiwi', 'Maracuyá', 'Guayaba', 'Mora', 'Arándano'
            ],
            'cereales_granos': [
                'Maíz', 'Arroz', 'Trigo', 'Cebada', 'Avena', 'Quinoa', 'Amaranto', 'Sorgo'
            ],
            'leguminosas': [
                'Frijol', 'Lenteja', 'Garbanzo', 'Arveja', 'Haba', 'Soya'
            ],
            'tuberculos': [
                'Yuca', 'Camote', 'Ñame', 'Malanga'
            ],
            'hierbas_aromaticas': [
                'Albahaca', 'Romero', 'Tomillo', 'Orégano', 'Menta', 'Hierbabuena'
            ],
            'otros': [
                'Café', 'Cacao', 'Caña de Azúcar', 'Chía', 'Ajonjolí', 'Girasol'
            ]
        }
        
        products = []
        product_names = []
        for categoria, nombres in productos_por_categoria.items():
            for nombre in nombres:
                product = Product.objects.create(nombre=nombre, categoria=categoria)
                products.append(product)
                product_names.append(nombre)
        self.stdout.write(f'{len(products)} productos base creados.')

        # --- Crear 20 Productores con Cultivos y Publicaciones ---
        producer_users = []
        for i in range(20):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f'prod_{first_name.lower()}{i}'
            email = f'{username}@example.com'
            
            user = User.objects.create_user(
                username=username, email=email, password='password123',
                first_name=first_name, last_name=last_name, role='Productor'
            )
            producer_users.append(user)
            
            # Seleccionar departamento y ciudad aleatorios de Colombia
            departamento = random.choice(list(COLOMBIA_LOCATIONS.keys()))
            ciudad = random.choice(COLOMBIA_LOCATIONS[departamento])
            direccion_especifica = fake.street_name() if random.choice([True, False]) else ""
            
            ProducerProfile.objects.create(
                user=user, 
                departamento=departamento,
                ciudad=ciudad,
                direccion=direccion_especifica,
                farm_description=fake.text(max_nb_chars=150),
                main_crops=random.choice(product_names)
            )
            self.stdout.write(f'Productor creado: {username}')

            # Crear 2 a 5 cultivos por productor
            for _ in range(random.randint(2, 5)):
                crop_status = random.choice(['listo_cosecha', 'cosechado', 'en_crecimiento'])
                estimated_quantity = random.randint(20, 1000)
                producto_nombre = random.choice(product_names)
                
                # Seleccionar unidad de medida apropiada según el producto
                if producto_nombre in ['Tomate', 'Fresa', 'Uva', 'Mora', 'Arándano']:
                    unidad = random.choice(['kg', 'cajas'])
                elif producto_nombre in ['Papa', 'Cebolla', 'Zanahoria', 'Yuca']:
                    unidad = random.choice(['kg', 'bultos', 'arrobas'])
                elif producto_nombre in ['Maíz', 'Arroz', 'Trigo', 'Frijol']:
                    unidad = random.choice(['kg', 'bultos', 'toneladas'])
                elif producto_nombre in ['Lechuga', 'Repollo', 'Coliflor', 'Brócoli']:
                    unidad = random.choice(['unidades', 'cajas'])
                else:
                    unidad = random.choice(['kg', 'cajas', 'unidades'])
                
                # Asignar categoría basada en el producto
                categoria_producto = 'otros'
                if producto_nombre in ['Papa', 'Tomate', 'Lechuga', 'Zanahoria', 'Cebolla', 'Pimiento', 'Pepino', 'Brócoli', 'Coliflor', 'Repollo', 'Espinaca', 'Rábano', 'Apio', 'Berenjena', 'Calabacín', 'Calabaza', 'Remolacha', 'Nabo', 'Puerro', 'Ajo', 'Acelga', 'Cilantro', 'Perejil']:
                    categoria_producto = 'hortalizas'
                elif producto_nombre in ['Aguacate', 'Fresa', 'Manzana', 'Pera', 'Durazno', 'Ciruela', 'Uva', 'Naranja', 'Limón', 'Mandarina', 'Toronja', 'Mango', 'Papaya', 'Piña', 'Banano', 'Plátano', 'Sandía', 'Melón', 'Kiwi', 'Maracuyá', 'Guayaba', 'Mora', 'Arándano']:
                    categoria_producto = 'frutas'
                elif producto_nombre in ['Maíz', 'Arroz', 'Trigo', 'Cebada', 'Avena', 'Quinoa', 'Amaranto', 'Sorgo']:
                    categoria_producto = 'cereales_granos'
                elif producto_nombre in ['Frijol', 'Lenteja', 'Garbanzo', 'Arveja', 'Haba', 'Soya']:
                    categoria_producto = 'leguminosas'
                elif producto_nombre in ['Yuca', 'Camote', 'Ñame', 'Malanga']:
                    categoria_producto = 'tuberculos'
                elif producto_nombre in ['Albahaca', 'Romero', 'Tomillo', 'Orégano', 'Menta', 'Hierbabuena']:
                    categoria_producto = 'hierbas_aromaticas'
                
                crop = Crop.objects.create(
                    nombre_producto=producto_nombre,
                    categoria=categoria_producto,
                    productor=user,
                    cantidad_estimada=estimated_quantity,
                    unidad_medida=unidad,
                    estado=crop_status,
                    fecha_disponibilidad=timezone.now().date() + timedelta(days=random.randint(-15, 30)),
                    notas=fake.text(max_nb_chars=100) if random.choice([True, False]) else None
                )

                # Crear una publicación para los cultivos listos (80% de probabilidad)
                if crop_status in ['listo_cosecha', 'cosechado'] and random.random() < 0.8:
                    # Precios más realistas según el producto
                    if producto_nombre in ['Café', 'Cacao', 'Quinoa', 'Chía']:
                        precio_base = random.uniform(8.0, 25.0)
                    elif producto_nombre in ['Aguacate', 'Fresa', 'Mora', 'Arándano']:
                        precio_base = random.uniform(3.0, 12.0)
                    elif producto_nombre in ['Hierbas Aromáticas', 'Albahaca', 'Romero', 'Tomillo']:
                        precio_base = random.uniform(15.0, 40.0)
                    elif producto_nombre in ['Papa', 'Yuca', 'Cebolla', 'Zanahoria']:
                        precio_base = random.uniform(0.8, 3.0)
                    else:
                        precio_base = random.uniform(1.5, 8.0)
                    
                    cantidad_disponible = max(1, estimated_quantity - random.randint(0, int(estimated_quantity * 0.3)))
                    
                    descripcion_opciones = [
                        f"Producto fresco de excelente calidad, cultivado de manera orgánica.",
                        f"Cosecha reciente, ideal para {random.choice(['restaurantes', 'supermercados', 'distribuidores'])}.",
                        f"Producto seleccionado, sin químicos, directo del campo.",
                        f"Calidad premium, perfecto para consumo inmediato.",
                        f"Cultivo tradicional, con métodos sostenibles."
                    ]
                    
                    Publication.objects.create(
                        cultivo=crop,
                        precio_por_unidad=round(precio_base, 2),
                        cantidad_disponible=cantidad_disponible,
                        cantidad_minima=random.randint(1, 10),
                        estado='disponible',
                        descripcion=random.choice(descripcion_opciones)
                    )
                    self.stdout.write(f'  -> Publicación creada para {cantidad_disponible} {unidad} de {crop.nombre_producto}')

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
            
            # Seleccionar departamento y ciudad aleatorios de Colombia para compradores
            departamento = random.choice(list(COLOMBIA_LOCATIONS.keys()))
            ciudad = random.choice(COLOMBIA_LOCATIONS[departamento])
            
            BuyerProfile.objects.create(
                user=user, 
                company_name=fake.company(),
                business_type=random.choice(['Restaurante', 'Supermercado', 'Distribuidor', 'Tienda Local', 'Mercado', 'Exportador']),
                departamento=departamento,
                ciudad=ciudad
            )
            self.stdout.write(f'Comprador creado: {username}')

        self.stdout.write(self.style.SUCCESS('¡Datos ficticios creados exitosamente!'))
