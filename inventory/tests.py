from django.test import TestCase
from django.utils import timezone
from inventory.models import Producto, Lote, ProductoTipo, ProductoMarca

class ProductoUpdatePoseeExistenciasTests(TestCase):
    def setUp(self):
        tipo = ProductoTipo.objects.create(nombre="Test Tipo")
        marca = ProductoMarca.objects.create(nombre="Test Marca")
        self.producto = Producto.objects.create(nombre="Test Producto", tipo=tipo, marca=marca)

    def test_creating_lote_sets_posee_existencias_true(self):
        lote = Lote.objects.create(producto=self.producto, fe_exp=timezone.now() + timezone.timedelta(days=10), consumido=False)
        self.producto.refresh_from_db()
        self.assertTrue(self.producto.get_posee_existencias)

    def test_consuming_all_lotes_sets_posee_existencias_false(self):
        lote = Lote.objects.create(producto=self.producto, fe_exp=timezone.now() + timezone.timedelta(days=10), consumido=False)
        self.producto.refresh_from_db()
        self.assertTrue(self.producto.get_posee_existencias)
        
        lote.consumido = True
        lote.save()
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.get_posee_existencias)

    def test_expired_lotes_do_not_affect_posee_existencias(self):
        lote = Lote.objects.create(producto=self.producto, fe_exp=timezone.now() - timezone.timedelta(days=1), consumido=False)
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.get_posee_existencias)
        
        lote2 = Lote.objects.create(producto=self.producto, fe_exp=timezone.now() + timezone.timedelta(days=10), consumido=False)
        self.producto.refresh_from_db()
        self.assertTrue(self.producto.get_posee_existencias)
        
    def test_deleting_lote_updates_posee_existencias(self):
        lote = Lote.objects.create(producto=self.producto, fe_exp=timezone.now() + timezone.timedelta(days=10), consumido=False)
        self.producto.refresh_from_db()
        self.assertTrue(self.producto.get_posee_existencias)
        
        lote.delete()
        self.producto.refresh_from_db()
        self.assertFalse(self.producto.get_posee_existencias)