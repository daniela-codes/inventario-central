from django.urls import reverse
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