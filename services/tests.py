from django.utils import timezone
from django.test import TestCase
from customers.models import Cliente
from services.models import Servicio, ServicioRealizado


class ServicioRealizadoTestCase(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nombre="John Doe")
        self.servicio = Servicio.objects.create(nombre="Service 1")
        self.servicio_realizado = ServicioRealizado.objects.create(
            cliente=self.cliente,
            servicio=self.servicio,
            fecha=timezone.now(),
            pagado=True,
            finalizado=False,
        )

    def test_str_representation(self):
        self.assertEqual(
            str(self.servicio_realizado), f"{self.cliente} - {self.servicio}"
        )

    def test_default_values(self):
        self.assertEqual(self.servicio_realizado.pagado, True)
        self.assertEqual(self.servicio_realizado.finalizado, False)

