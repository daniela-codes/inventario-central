from django.contrib import admin
from .models import Categoria, Proveedor, Producto, MovimientoInventario


# Configuración del modelo Categoria en el panel de administración.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)


# Configuración del modelo Proveedor en el panel de administración.
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono', 'correo')
    search_fields = ('nombre', 'correo')


# Configuración del modelo Producto en el panel de administración.
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'stock', 'precio', 'categoria', 'proveedor')
    search_fields = ('nombre',)
    list_filter = ('categoria', 'proveedor')


# Configuración del modelo MovimientoInventario en el panel de administración.
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'tipo', 'cantidad', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('producto__nombre',)