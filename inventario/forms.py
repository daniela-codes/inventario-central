from django import forms
from django.core.exceptions import ValidationError

from .models import Categoria, MovimientoInventario, Producto, Proveedor


class StyledModelForm(forms.ModelForm):
    """Aplica las clases visuales del panel sin librerías externas."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = 'form-control'
            if isinstance(field.widget, forms.Textarea):
                css_class += ' form-textarea'
                field.widget.attrs.setdefault('rows', 3)
            field.widget.attrs['class'] = css_class


class ProductoForm(StyledModelForm):
    class Meta:
        model = Producto
        fields = (
            'nombre', 'descripcion', 'stock', 'stock_minimo', 'precio',
            'categoria', 'proveedor',
        )
        labels = {'stock_minimo': 'Stock mínimo'}
        widgets = {
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'stock': forms.NumberInput(attrs={'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'min': '0'}),
        }

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise ValidationError('El precio debe ser mayor que cero.')
        return precio


class CategoriaForm(StyledModelForm):
    class Meta:
        model = Categoria
        fields = ('nombre', 'descripcion')


class ProveedorForm(StyledModelForm):
    class Meta:
        model = Proveedor
        fields = ('nombre', 'telefono', 'correo', 'direccion')


class MovimientoForm(StyledModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ('producto', 'tipo', 'cantidad', 'observacion')
        widgets = {'cantidad': forms.NumberInput(attrs={'min': '1'})}

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor que cero.')
        return cantidad

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        tipo = cleaned_data.get('tipo')
        cantidad = cleaned_data.get('cantidad')
        if producto and tipo == 'SALIDA' and cantidad and cantidad > producto.stock:
            self.add_error(
                'cantidad',
                f'No hay stock suficiente. Disponible: {producto.stock} unidades.',
            )
        return cleaned_data
