from django.core.management.base import BaseCommand
from inventario.models import Categoria, Proveedor, Producto, MovimientoInventario


class Command(BaseCommand):
    help = 'Carga datos de prueba para Inventario Central'

    def handle(self, *args, **kwargs):
        # Categorías principales del sistema.
        oficina, _ = Categoria.objects.get_or_create(
            nombre='Materiales de oficina',
            defaults={
                'descripcion': 'Productos utilizados para labores administrativas e institucionales.'
            }
        )

        pedagogicos, _ = Categoria.objects.get_or_create(
            nombre='Materiales pedagógicos',
            defaults={
                'descripcion': 'Recursos utilizados para actividades educativas y de apoyo al aprendizaje.'
            }
        )

        aseo, _ = Categoria.objects.get_or_create(
            nombre='Materiales de aseo',
            defaults={
                'descripcion': 'Insumos destinados a limpieza, higiene y mantención de espacios.'
            }
        )

        # Proveedores asociados al inventario.
        proveedor_oficina, _ = Proveedor.objects.get_or_create(
            nombre='Distribuidora Central',
            defaults={
                'telefono': '+56911111111',
                'correo': 'contacto@distribuidoracentral.cl',
                'direccion': 'La Serena, Chile'
            }
        )

        proveedor_pedagogico, _ = Proveedor.objects.get_or_create(
            nombre='Proveedor Educativo Norte',
            defaults={
                'telefono': '+56922222222',
                'correo': 'ventas@educativonorte.cl',
                'direccion': 'Coquimbo, Chile'
            }
        )

        proveedor_aseo, _ = Proveedor.objects.get_or_create(
            nombre='Insumos de Aseo Norte',
            defaults={
                'telefono': '+56933333333',
                'correo': 'ventas@aseonorte.cl',
                'direccion': 'La Serena, Chile'
            }
        )

        # Lista de productos basada en materiales reales.
        productos = [
            {
                'nombre': 'Archivador carta ancho burdeo',
                'descripcion': 'Archivador para organización de documentos administrativos.',
                'stock': 24,
                'precio': 2490,
                'categoria': oficina,
                'proveedor': proveedor_oficina,
            },
            {
                'nombre': 'Calculadora 12 dígitos',
                'descripcion': 'Calculadora de escritorio para labores administrativas.',
                'stock': 8,
                'precio': 6990,
                'categoria': oficina,
                'proveedor': proveedor_oficina,
            },
            {
                'nombre': 'Corchetera metálica mediana',
                'descripcion': 'Corchetera metálica para uso de oficina.',
                'stock': 12,
                'precio': 3990,
                'categoria': oficina,
                'proveedor': proveedor_oficina,
            },
            {
                'nombre': 'Corrector lápiz 8 ml',
                'descripcion': 'Corrector en formato lápiz para documentos escritos.',
                'stock': 30,
                'precio': 1290,
                'categoria': oficina,
                'proveedor': proveedor_oficina,
            },
            {
                'nombre': 'Resma fotocopia carta 75g 500 hojas',
                'descripcion': 'Resma de papel tamaño carta para impresión y fotocopias.',
                'stock': 40,
                'precio': 4990,
                'categoria': oficina,
                'proveedor': proveedor_oficina,
            },
            {
                'nombre': 'Pendrive 16GB USB',
                'descripcion': 'Unidad de almacenamiento USB para respaldo de información.',
                'stock': 10,
                'precio': 5990,
                'categoria': oficina,
                'proveedor': proveedor_oficina,
            },
            {
                'nombre': 'Acuarela 12 color',
                'descripcion': 'Set de acuarelas para actividades artísticas.',
                'stock': 18,
                'precio': 2990,
                'categoria': pedagogicos,
                'proveedor': proveedor_pedagogico,
            },
            {
                'nombre': 'Block dibujo liceo 60 20 hojas',
                'descripcion': 'Block de dibujo para actividades pedagógicas.',
                'stock': 25,
                'precio': 2190,
                'categoria': pedagogicos,
                'proveedor': proveedor_pedagogico,
            },
            {
                'nombre': 'Cuaderno universitario matemática 7 mm 100 hojas',
                'descripcion': 'Cuaderno universitario cuadriculado para uso escolar.',
                'stock': 35,
                'precio': 1890,
                'categoria': pedagogicos,
                'proveedor': proveedor_pedagogico,
            },
            {
                'nombre': 'Lápiz color 12 colores',
                'descripcion': 'Caja de lápices de colores para actividades escolares.',
                'stock': 28,
                'precio': 2590,
                'categoria': pedagogicos,
                'proveedor': proveedor_pedagogico,
            },
            {
                'nombre': 'Plumones de pizarra recargable azul',
                'descripcion': 'Plumón recargable para uso en pizarra.',
                'stock': 22,
                'precio': 1490,
                'categoria': pedagogicos,
                'proveedor': proveedor_pedagogico,
            },
            {
                'nombre': 'Témpera 12 color 15 ml',
                'descripcion': 'Set de témperas para trabajos manuales y artísticos.',
                'stock': 16,
                'precio': 3490,
                'categoria': pedagogicos,
                'proveedor': proveedor_pedagogico,
            },
            {
                'nombre': 'Tijera ergonómica 5,5 pulgadas',
                'descripcion': 'Tijera escolar ergonómica para actividades pedagógicas.',
                'stock': 20,
                'precio': 1990,
                'categoria': pedagogicos,
                'proveedor': proveedor_pedagogico,
            },
            {
                'nombre': 'Alcohol gel 1 litro',
                'descripcion': 'Alcohol gel para higiene de manos.',
                'stock': 15,
                'precio': 3990,
                'categoria': aseo,
                'proveedor': proveedor_aseo,
            },
            {
                'nombre': 'Amonio cuaternario 1 litro',
                'descripcion': 'Producto desinfectante para superficies.',
                'stock': 12,
                'precio': 4590,
                'categoria': aseo,
                'proveedor': proveedor_aseo,
            },
            {
                'nombre': 'Bolsa de basura 70x90 cm rollo 10 unidades',
                'descripcion': 'Bolsas de basura para mantención de espacios.',
                'stock': 30,
                'precio': 2590,
                'categoria': aseo,
                'proveedor': proveedor_aseo,
            },
            {
                'nombre': 'Cloro líquido 1 litro',
                'descripcion': 'Cloro líquido para limpieza y desinfección.',
                'stock': 24,
                'precio': 1290,
                'categoria': aseo,
                'proveedor': proveedor_aseo,
            },
            {
                'nombre': 'Dispensador de jabón 500 ml',
                'descripcion': 'Dispensador para jabón líquido de baño.',
                'stock': 6,
                'precio': 5990,
                'categoria': aseo,
                'proveedor': proveedor_aseo,
            },
            {
                'nombre': 'Escobillón clásico con mango',
                'descripcion': 'Escobillón para limpieza de espacios interiores.',
                'stock': 10,
                'precio': 3490,
                'categoria': aseo,
                'proveedor': proveedor_aseo,
            },
            {
                'nombre': 'Papel higiénico jumbo 500 metros',
                'descripcion': 'Papel higiénico jumbo para baños institucionales.',
                'stock': 18,
                'precio': 8990,
                'categoria': aseo,
                'proveedor': proveedor_aseo,
            },
            {
                'nombre': 'Toalla de papel 250 mts 2 rollos',
                'descripcion': 'Toalla de papel para limpieza e higiene.',
                'stock': 14,
                'precio': 7490,
                'categoria': aseo,
                'proveedor': proveedor_aseo,
            },
        ]

        for item in productos:
            Producto.objects.update_or_create(
                nombre=item['nombre'],
                defaults=item
            )

        # Se eliminan movimientos anteriores para evitar duplicados al ejecutar nuevamente.
        MovimientoInventario.objects.all().delete()

        movimientos = [
            {
                'producto': Producto.objects.get(nombre='Resma fotocopia carta 75g 500 hojas'),
                'tipo': 'ENTRADA',
                'cantidad': 20,
                'observacion': 'Ingreso inicial de resmas al inventario.'
            },
            {
                'producto': Producto.objects.get(nombre='Plumones de pizarra recargable azul'),
                'tipo': 'SALIDA',
                'cantidad': 5,
                'observacion': 'Entrega de plumones para sala de clases.'
            },
            {
                'producto': Producto.objects.get(nombre='Alcohol gel 1 litro'),
                'tipo': 'ENTRADA',
                'cantidad': 10,
                'observacion': 'Ingreso de insumos de higiene.'
            },
            {
                'producto': Producto.objects.get(nombre='Bolsa de basura 70x90 cm rollo 10 unidades'),
                'tipo': 'SALIDA',
                'cantidad': 4,
                'observacion': 'Entrega de bolsas para mantención.'
            },
            {
                'producto': Producto.objects.get(nombre='Témpera 12 color 15 ml'),
                'tipo': 'SALIDA',
                'cantidad': 3,
                'observacion': 'Entrega de materiales para actividad pedagógica.'
            },
        ]

        for movimiento in movimientos:
            MovimientoInventario.objects.create(**movimiento)

        self.stdout.write(
            self.style.SUCCESS('Datos demo cargados correctamente en Inventario Central.')
        )