from django.shortcuts import render
from django.db.models import Sum
from rest_framework import viewsets
from .models import Categoria, Proveedor, Producto, MovimientoInventario
from .serializers import (
    CategoriaSerializer,
    ProveedorSerializer,
    ProductoSerializer,
    MovimientoInventarioSerializer
)

# Vista principal del sistema.
def home(request):
    total_stock = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0

    contexto = {
        'total_categorias': Categoria.objects.count(),
        'total_proveedores': Proveedor.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_movimientos': MovimientoInventario.objects.count(),
        'total_stock': total_stock,
        'productos_con_stock': Producto.objects.filter(stock__gt=0).count(),
        'ultimos_productos': Producto.objects.select_related('categoria', 'proveedor').order_by('-fecha_creacion')[:5],
        'ultimos_movimientos': MovimientoInventario.objects.select_related('producto').order_by('-fecha')[:4],
    }

    return render(request, 'inventario/home.html', contexto)

# ViewSet para gestionar categorías desde la API.
class CategoriaViewSet(viewsets.ModelViewSet):
    """
    Permite listar, crear, consultar, actualizar y eliminar las categorías del inventario.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_view_name(self):
        return 'Categorías del inventario'


# ViewSet para gestionar proveedores desde la API.
class ProveedorViewSet(viewsets.ModelViewSet):
    """
    Permite administrar los proveedores asociados a los productos del sistema.
    """
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

    def get_view_name(self):
        return 'Proveedores del sistema'


# ViewSet para listar, crear, actualizar y eliminar productos.
class ProductoViewSet(viewsets.ModelViewSet):
    """
    Permite gestionar los productos disponibles en el inventario.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_view_name(self):
        return 'Productos del inventario'


# ViewSet para registrar entradas y salidas del inventario.
class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """
    Permite registrar los movimientos de entrada y salida de productos.
    """
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer

    def get_view_name(self):
        return 'Movimientos de inventario'