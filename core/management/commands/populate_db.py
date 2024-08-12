from datetime import datetime, timedelta
import os
import random
import string
from django.core.management.base import BaseCommand
from faker import Faker
from faker.providers import lorem, company, misc, python
import requests
from dotenv import load_dotenv
from customers.models import Cliente
from lib.faker import faker_commerce, beauty_provider
from inventory.models import Producto, ProductoTipo, ProductoMarca, ProductoImg, Lote
from services.models import Servicio
from staff.models import Personal
from django.contrib.auth.models import User

load_dotenv()
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")


def generar_sku(prefijo="SKU", longitud_cuerpo=6, sufijo=None):
    cuerpo = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=longitud_cuerpo)
    )
    if sufijo:
        return f"{prefijo}-{cuerpo}-{sufijo}"
    else:
        return f"{prefijo}-{cuerpo}"


def obtener_imagenes_unsplash(query, cantidad=10):
    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={UNSPLASH_ACCESS_KEY}&per_page={cantidad}"
    response = requests.get(url)
    data = response.json()
    return [img["urls"]["regular"] for img in data["results"]]


class Command(BaseCommand):
    help = "Popula la base de datos con datos de prueba usando Faker"

    def populate_producto(self, fake: Faker):
        for _ in range(50):
            producto, tipo_nombre = fake.beauty_product()
            tipo, _ = ProductoTipo.objects.get_or_create(
                nombre=tipo_nombre, descripcion=fake.sentence(nb_words=10)
            )
            marca_nombre = fake.beauty_brand()
            marca, _ = ProductoMarca.objects.get_or_create(nombre=marca_nombre)
            Producto.objects.create(
                tipo=tipo,
                marca=marca,
                nombre=producto,
                sku=generar_sku(),
                precio=fake.pydecimal(min_value=0, right_digits=2, left_digits=4),
                usos_est=random.randint(1, 10),
            )

    def populate_lote(self, fake: Faker):
        productos = Producto.objects.active().all()

        for prod in productos:
            try:
                Lote.objects.create(
                    producto=prod,
                    fe_compra=datetime.now(),
                    fe_exp=fake.date_between(start_date="+1y", end_date="+3y"),
                    cant=random.randint(1, 10),
                    costo=fake.pydecimal(min_value=0, right_digits=2, left_digits=4),
                )
            except:
                pass

    def populate_producto_img(self, fake: Faker):
        productos = Producto.objects.active().all()
        imagenes_por_tipo = {
            "Cuidado del Cabello": obtener_imagenes_unsplash("hair care product"),
            "Cuidado de la Piel": obtener_imagenes_unsplash("skin care product"),
            "Maquillaje": obtener_imagenes_unsplash("makeup product"),
            "Fragancias": obtener_imagenes_unsplash("fragrance product"),
            "Cuidado Corporal": obtener_imagenes_unsplash("body care product"),
        }
        for prod in productos:
            tipo_nombre = prod.tipo.nombre
            if tipo_nombre in imagenes_por_tipo:
                url_imagen = random.choice(imagenes_por_tipo[tipo_nombre])
                ProductoImg.objects.create(
                    producto=prod,
                    url_imagen_externa=url_imagen,
                    is_cover=True,
                )

    def populate_cliente(self, fake: Faker):
        for _ in range(10):
            Cliente.objects.create(
                nombre=fake.first_name(),
                apellido=fake.last_name(),
            )

    def populate_personal(self, fake: Faker):
        for _ in range(5):
            Personal.objects.create(
                nombre=fake.first_name(),
                apellido=fake.last_name(),
                cedula=fake.unique.random_number(digits=10),
            )

    def populate_servicio(self, fake: Faker):
        servicios_generados = set()

        while len(servicios_generados) < 5:
            servicio, tipo = fake.beauty_service()
            if servicio not in servicios_generados:
                servicios_generados.add(servicio)
                Servicio.objects.create(
                    nombre=servicio,
                    descripcion=fake.text(),
                    precio=fake.pydecimal(
                        min_value=0, max_value=25, right_digits=2, left_digits=4
                    ),
                    tiempo_est=timedelta(minutes=fake.random_int(min=30, max=180)),
                )

    def create_superuser(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin", email="admin@antonella.com", password="1234"
            )

    def populate_data(self):
        fake = Faker(["es_ES"])
        fake.add_provider(faker_commerce.Provider)
        fake.add_provider(beauty_provider.Provider)
        fake.add_provider(lorem)
        fake.add_provider(company)
        fake.add_provider(misc)
        fake.add_provider(python)

        self.create_superuser()
        self.populate_producto(fake)
        self.populate_producto_img(fake)
        self.populate_cliente(fake)
        self.populate_personal(fake)
        self.populate_servicio(fake)

    def handle(self, *args, **kwargs):
        self.populate_data()

        self.stdout.write(self.style.SUCCESS(f"Successfully created records"))
