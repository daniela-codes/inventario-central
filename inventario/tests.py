from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Categoria, Proveedor, Producto, MovimientoInventario


class InventarioAPITestCase(APITestCase):
    def setUp(self):
        # Datos base para usar en las pruebas.
        self.categoria = Categoria.objects.create(
            nombre='Materiales de oficina',
            descripcion='Productos utilizados para labores administrativas.'
        )

        self.proveedor = Proveedor.objects.create(
            nombre='Distribuidora Central',
            telefono='+56911111111',
            correo='contacto@distribuidoracentral.cl',
            direccion='La Serena, Chile'
        )

        self.producto = Producto.objects.create(
            nombre='Resma fotocopia carta',
            descripcion='Resma de papel tamaño carta.',
            stock=20,
            precio=4990,
            categoria=self.categoria,
            proveedor=self.proveedor
        )

    def test_listar_productos(self):
        # Verifica que el endpoint de productos responda correctamente.
        url = reverse('producto-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_producto(self):
        # Verifica que se pueda crear un producto desde la API.
        url = reverse('producto-list')

        data = {
            'nombre': 'Archivador carta ancho burdeo',
            'descripcion': 'Archivador para documentos administrativos.',
            'stock': 15,
            'precio': 2490,
            'categoria': self.categoria.id,
            'proveedor': self.proveedor.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 2)

    def test_no_permitir_producto_con_precio_cero(self):
        # Verifica la validación del serializer para precio inválido.
        url = reverse('producto-list')

        data = {
            'nombre': 'Producto inválido',
            'descripcion': 'Producto con precio incorrecto.',
            'stock': 10,
            'precio': 0,
            'categoria': self.categoria.id,
            'proveedor': self.proveedor.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_permitir_eliminar_categoria_con_productos_asociados(self):
        url = reverse('categoria-detail', args=[self.categoria.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            Categoria.objects.filter(pk=self.categoria.pk).exists()
        )
        self.assertTrue(
            Producto.objects.filter(pk=self.producto.pk).exists()
        )

    def test_permitir_eliminar_categoria_sin_productos(self):
        categoria = Categoria.objects.create(
            nombre='Categoria temporal',
            descripcion='Categoria sin productos asociados.'
        )
        url = reverse('categoria-detail', args=[categoria.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Categoria.objects.filter(pk=categoria.pk).exists()
        )

    def test_eliminar_proveedor_mantiene_producto_sin_proveedor(self):
        url = reverse('proveedor-detail', args=[self.proveedor.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Proveedor.objects.filter(pk=self.proveedor.pk).exists()
        )

        self.producto.refresh_from_db()
        self.assertTrue(
            Producto.objects.filter(pk=self.producto.pk).exists()
        )
        self.assertIsNone(self.producto.proveedor)

    def test_no_permitir_categoria_duplicada(self):
        url = reverse('categoria-list')

        data = {
            'nombre': self.categoria.nombre,
            'descripcion': 'Intento de categoria duplicada.'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            Categoria.objects.filter(nombre=self.categoria.nombre).count(),
            1
        )

    def test_no_permitir_proveedor_con_correo_invalido(self):
        url = reverse('proveedor-list')

        data = {
            'nombre': 'Proveedor correo invalido',
            'telefono': '+56922222222',
            'correo': 'correo-no-valido',
            'direccion': 'La Serena'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Proveedor.objects.filter(nombre='Proveedor correo invalido').exists()
        )

    def test_crear_categoria_por_api(self):
        url = reverse('categoria-list')

        data = {
            'nombre': 'Herramientas',
            'descripcion': 'Herramientas y accesorios.'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Categoria.objects.filter(nombre='Herramientas').exists()
        )

    def test_editar_categoria_por_api(self):
        url = reverse('categoria-detail', args=[self.categoria.pk])

        data = {
            'nombre': 'Materiales administrativos',
            'descripcion': 'Categoria actualizada.'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.categoria.refresh_from_db()
        self.assertEqual(
            self.categoria.nombre,
            'Materiales administrativos'
        )

    def test_crear_proveedor_por_api(self):
        url = reverse('proveedor-list')

        data = {
            'nombre': 'Proveedor Norte',
            'telefono': '+56933333333',
            'correo': 'contacto@proveedornorte.cl',
            'direccion': 'Coquimbo'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Proveedor.objects.filter(nombre='Proveedor Norte').exists()
        )

    def test_editar_proveedor_por_api(self):
        url = reverse('proveedor-detail', args=[self.proveedor.pk])

        data = {
            'nombre': 'Distribuidora Central Actualizada',
            'telefono': '+56944444444'
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.proveedor.refresh_from_db()
        self.assertEqual(
            self.proveedor.nombre,
            'Distribuidora Central Actualizada'
        )
        self.assertEqual(
            self.proveedor.telefono,
            '+56944444444'
        )

    def test_crear_movimiento_inventario(self):
        # Verifica que se pueda registrar un movimiento de inventario.
        url = reverse('movimientoinventario-list')

        data = {
            'producto': self.producto.id,
            'tipo': 'ENTRADA',
            'cantidad': 5,
            'observacion': 'Ingreso de productos al inventario.'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MovimientoInventario.objects.count(), 1)

    def test_no_permitir_movimiento_con_cantidad_cero(self):
        # Verifica la validación del serializer para cantidad inválida.
        url = reverse('movimientoinventario-list')

        data = {
            'producto': self.producto.id,
            'tipo': 'SALIDA',
            'cantidad': 0,
            'observacion': 'Movimiento inválido.'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eliminar_salida_restaura_el_stock_por_api(self):
        # El producto ya refleja la salida registrada en su stock actual.
        self.producto.stock = 17
        self.producto.save(update_fields=['stock'])
        movimiento = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo='SALIDA',
            cantidad=3,
        )

        url = reverse('movimientoinventario-detail', args=[movimiento.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 20)
        self.assertFalse(MovimientoInventario.objects.filter(pk=movimiento.pk).exists())

    def test_no_permitir_eliminar_entrada_si_deja_stock_negativo(self):
        self.producto.stock = 3
        self.producto.save(update_fields=['stock'])
        movimiento = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo='ENTRADA',
            cantidad=5,
        )

        url = reverse('movimientoinventario-detail', args=[movimiento.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertTrue(MovimientoInventario.objects.filter(pk=movimiento.pk).exists())

    def test_eliminar_entrada_descuenta_stock_por_api(self):
        self.producto.stock = 25
        self.producto.save(update_fields=['stock'])
        movimiento = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo='ENTRADA',
            cantidad=5,
        )

        url = reverse('movimientoinventario-detail', args=[movimiento.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 20)


class MovimientosWebTestCase(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('operador', password='clave-segura')
        self.client.force_login(self.usuario)
        self.categoria = Categoria.objects.create(nombre='Aseo')
        self.producto = Producto.objects.create(
            nombre='Jabón líquido',
            stock=20,
            precio=2500,
            categoria=self.categoria,
        )

    def test_filtrar_movimientos_por_rango_de_fechas(self):
        antiguo = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo='ENTRADA',
            cantidad=4,
        )
        reciente = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo='SALIDA',
            cantidad=2,
        )
        MovimientoInventario.objects.filter(pk=antiguo.pk).update(
            fecha=timezone.now() - timedelta(days=10)
        )

        fecha_hoy = timezone.localdate().isoformat()
        response = self.client.get(
            reverse('movimientos'),
            {'fecha_desde': fecha_hoy, 'fecha_hasta': fecha_hoy},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        movimientos = response.context['pagina'].object_list
        self.assertEqual(list(movimientos), [reciente])

    def test_rechazar_rango_de_fechas_invertido(self):
        response = self.client.get(
            reverse('movimientos'),
            {'fecha_desde': '2026-09-10', 'fecha_hasta': '2026-09-01'},
            follow=True,
        )

        self.assertContains(
            response,
            'La fecha inicial no puede ser posterior a la fecha final.',
        )

    def test_eliminar_salida_desde_la_interfaz_restaura_stock(self):
        self.producto.stock = 15
        self.producto.save(update_fields=['stock'])
        movimiento = MovimientoInventario.objects.create(
            producto=self.producto,
            tipo='SALIDA',
            cantidad=5,
        )

        response = self.client.post(
            reverse('movimiento_eliminar', args=[movimiento.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 20)
        self.assertFalse(MovimientoInventario.objects.filter(pk=movimiento.pk).exists())
