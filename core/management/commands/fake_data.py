import random
import string
from django.core.management.base import BaseCommand
from faker import Faker
from faker.providers import lorem, company, misc, python
import faker_commerce
from inventory.models import Producto, ProductoTipo, ProductoMarca, ProductoImg, Lote


def generar_sku(prefijo="SKU", longitud_cuerpo=6, sufijo=None):
    cuerpo = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=longitud_cuerpo)
    )
    if sufijo:
        return f"{prefijo}-{cuerpo}-{sufijo}"
    else:
        return f"{prefijo}-{cuerpo}"


class Command(BaseCommand):
    help = "Popula la base de datos con datos de prueba usando Faker"

    def populate_producto_tipo(self, fake: Faker):
        for _ in range(5):
            ProductoTipo.objects.create(
                nombre=fake.ecommerce_category(), descripcion=fake.sentence(nb_words=10)
            )

    def populate_producto_marca(self, fake: Faker):
        for _ in range(10):
            ProductoMarca.objects.create(nombre=fake.company())

    def populate_producto(self, fake: Faker):
        productoTipo = ProductoTipo.objects.active().all()
        productoMarca = ProductoMarca.objects.active().all()
        for _ in range(50):
            Producto.objects.create(
                tipo=random.choice(productoTipo),
                marca=random.choice(productoMarca),
                nombre=fake.ecommerce_name(),
                sku=generar_sku(),
                precio=fake.pydecimal(min_value=0, right_digits=2, left_digits=4),
                usos_est=random.randint(1, 10),
            )

    def populate_producto_img(self, fake: Faker):
        productos = Producto.objects.active().all()
        for prod in productos:
            ProductoImg.objects.create(
                producto=prod,
                url_imagen_externa=f"https://picsum.photos/id/{fake.unique.pyint(min_value=0, max_value=1000)}/300/300",
                is_cover=True,
            )

    def populate_data(self):
        fake = Faker(["es_ES"])
        fake.add_provider(faker_commerce.Provider)
        fake.add_provider(lorem)
        fake.add_provider(company)
        fake.add_provider(misc)
        fake.add_provider(python)

        self.populate_producto_tipo(fake)
        self.populate_producto_marca(fake)
        self.populate_producto(fake)
        self.populate_producto_img(fake)

    def handle(self, *args, **kwargs):
        self.populate_data()

        self.stdout.write(self.style.SUCCESS(f"Successfully created records"))
