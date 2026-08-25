from rest_framework import serializers
from .models import Categoria, Proveedor, Producto, MovimientoInventario


# Serializer para mostrar y recibir datos de categorías.
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


# Serializer para mostrar y recibir datos de proveedores.
class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'


# Serializer principal para los productos del inventario.
class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(
        source='categoria.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True
    )

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'stock',
            'precio',
            'categoria',
            'categoria_nombre',
            'proveedor',
            'proveedor_nombre',
            'fecha_creacion',
        ]

    # Validación para evitar precios iguales o menores a cero.
    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El precio debe ser mayor a cero.'
            )
        return value


# Serializer para registrar entradas y salidas de inventario.
class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(
        source='producto.nombre',
        read_only=True
    )

    class Meta:
        model = MovimientoInventario
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'tipo',
            'cantidad',
            'fecha',
            'observacion',
        ]

    # Validación para evitar movimientos con cantidad cero.
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'La cantidad debe ser mayor a cero.'
            )
        return value