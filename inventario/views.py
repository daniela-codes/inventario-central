from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, viewsets
from rest_framework.response import Response
from .models import Categoria, Proveedor, Producto, MovimientoInventario
from .forms import CategoriaForm, MovimientoForm, ProductoForm, ProveedorForm
from .serializers import (
    CategoriaSerializer,
    ProveedorSerializer,
    ProductoSerializer,
    MovimientoInventarioSerializer
)

# Vista de inicio de sesión.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        error = 'Usuario o contraseña incorrectos.'

    return render(
        request,
        'inventario/login.html',
        {'error': error}
    )


def logout_view(request):
    logout(request)
    return redirect('login')


# Vista principal del sistema.
@login_required(login_url='login')
def home(request):
    # Stock total de todos los productos
    total_stock = Producto.objects.aggregate(
        total=Sum('stock')
    )['total'] or 0

    # Movimientos de los últimos 30 días
    hace_30_dias = timezone.now() - timedelta(days=30)

    movimientos_30_dias = MovimientoInventario.objects.filter(
        fecha__gte=hace_30_dias
    )

    # Entradas y salidas
    total_entradas = movimientos_30_dias.filter(
        tipo='ENTRADA'
    ).count()

    total_salidas = movimientos_30_dias.filter(
        tipo='SALIDA'
    ).count()

    total_movimientos_30_dias = movimientos_30_dias.count()

    # Evitamos división por cero
    if total_movimientos_30_dias > 0:
        porcentaje_entradas = round(
            (total_entradas / total_movimientos_30_dias) * 100
        )
        porcentaje_salidas = round(
            (total_salidas / total_movimientos_30_dias) * 100
        )
    else:
        porcentaje_entradas = 0
        porcentaje_salidas = 0

    # Stock agrupado por categoría
    categorias_stock = list(
        Categoria.objects
        .annotate(total_stock=Sum('productos__stock'))
        .values('nombre', 'total_stock')
        .order_by('-total_stock')
    )

    # El mayor stock será el 100% del gráfico
    mayor_stock = max(
        [categoria['total_stock'] or 0 for categoria in categorias_stock],
        default=0
    )

    for categoria in categorias_stock:
        stock = categoria['total_stock'] or 0

        if mayor_stock > 0:
            categoria['porcentaje'] = round(
                (stock / mayor_stock) * 100
            )
        else:
            categoria['porcentaje'] = 0

        # Altura de la barra en píxeles
        categoria['altura'] = max(
            2,
            round(categoria['porcentaje'] * 1.5)
        )

    # Alertas: stock actual menor o igual al mínimo configurado.
    productos_alerta = (
        Producto.objects
        .filter(stock__lte=F('stock_minimo'))
        .select_related('categoria')
        .order_by('stock', 'nombre')
    )

    contexto = {
        'active_nav': 'dashboard',
        'total_categorias': Categoria.objects.count(),
        'total_proveedores': Proveedor.objects.count(),
        'total_productos': Producto.objects.count(),

        # Total histórico
        'total_movimientos': MovimientoInventario.objects.count(),

        'total_stock': total_stock,

        # Cantidad real de productos que requieren reposición.
        'productos_con_stock': productos_alerta.count(),

        # Productos que se mostrarán en el panel de alertas.
        'productos_alerta': productos_alerta[:5],

        # Datos para el gráfico de categorías
        'categorias_stock': categorias_stock,

        # Datos para el gráfico de entradas/salidas
        'total_entradas': total_entradas,
        'total_salidas': total_salidas,
        'total_movimientos_30_dias': total_movimientos_30_dias,
        'porcentaje_entradas': porcentaje_entradas,
        'porcentaje_salidas': porcentaje_salidas,

        # Últimos registros
        'ultimos_productos': Producto.objects
            .select_related('categoria', 'proveedor')
            .order_by('-fecha_creacion')[:5],

        'ultimos_movimientos': MovimientoInventario.objects
            .select_related('producto')
            .order_by('-fecha')[:5],
    }

    return render(
        request,
        'inventario/home.html',
        contexto
    )


# Vistas web del prototipo funcional. La API REST se mantiene disponible en /api/.
@login_required(login_url='login')
def productos(request):
    consulta = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    estado = request.GET.get('estado', '').strip()

    registros = Producto.objects.select_related('categoria', 'proveedor')
    if consulta:
        registros = registros.filter(
            Q(nombre__icontains=consulta)
            | Q(descripcion__icontains=consulta)
            | Q(proveedor__nombre__icontains=consulta)
        )
    if categoria_id:
        registros = registros.filter(categoria_id=categoria_id)
    if estado == 'bajo':
        registros = registros.filter(stock__lte=F('stock_minimo'))
    elif estado == 'disponible':
        registros = registros.filter(stock__gt=F('stock_minimo'))

    pagina = Paginator(registros.order_by('nombre'), 15).get_page(
        request.GET.get('page')
    )
    return render(request, 'inventario/productos.html', {
        'active_nav': 'productos',
        'pagina': pagina,
        'categorias': Categoria.objects.all(),
        'q': consulta,
        'categoria_seleccionada': categoria_id,
        'estado': estado,
        'total_filtrado': registros.count(),
    })


@login_required(login_url='login')
def producto_crear(request):
    form = ProductoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        producto = form.save()
        messages.success(request, f'Producto “{producto.nombre}” registrado correctamente.')
        return redirect('productos')
    return _render_form(request, form, 'Registrar producto', 'productos', 'productos')


@login_required(login_url='login')
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = ProductoForm(request.POST or None, instance=producto)
    if request.method == 'POST' and form.is_valid():
        producto = form.save()
        messages.success(request, f'Producto “{producto.nombre}” actualizado.')
        return redirect('productos')
    return _render_form(request, form, 'Editar producto', 'productos', 'productos')


@login_required(login_url='login')
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto “{nombre}” eliminado.')
        return redirect('productos')
    return _render_confirm(request, producto, 'producto', 'productos', 'productos')


@login_required(login_url='login')
def categorias(request):
    consulta = request.GET.get('q', '').strip()
    registros = Categoria.objects.annotate(
        total_productos=Count('productos'),
        total_stock=Sum('productos__stock'),
    )
    if consulta:
        registros = registros.filter(
            Q(nombre__icontains=consulta) | Q(descripcion__icontains=consulta)
        )
    return render(request, 'inventario/categorias.html', {
        'active_nav': 'categorias',
        'registros': registros,
        'q': consulta,
    })


@login_required(login_url='login')
def categoria_crear(request):
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        categoria = form.save()
        messages.success(request, f'Categoría “{categoria.nombre}” creada.')
        return redirect('categorias')
    return _render_form(request, form, 'Nueva categoría', 'categorias', 'categorias')


@login_required(login_url='login')
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST' and form.is_valid():
        categoria = form.save()
        messages.success(request, f'Categoría “{categoria.nombre}” actualizada.')
        return redirect('categorias')
    return _render_form(request, form, 'Editar categoría', 'categorias', 'categorias')


@login_required(login_url='login')
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        if categoria.productos.exists():
            messages.error(
                request,
                'No se puede eliminar una categoría que tiene productos asociados.',
            )
        else:
            nombre = categoria.nombre
            categoria.delete()
            messages.success(request, f'Categoría “{nombre}” eliminada.')
        return redirect('categorias')
    return _render_confirm(request, categoria, 'categoría', 'categorias', 'categorias')


@login_required(login_url='login')
def proveedores(request):
    consulta = request.GET.get('q', '').strip()
    registros = Proveedor.objects.annotate(total_productos=Count('productos'))
    if consulta:
        registros = registros.filter(
            Q(nombre__icontains=consulta)
            | Q(correo__icontains=consulta)
            | Q(telefono__icontains=consulta)
        )
    return render(request, 'inventario/proveedores.html', {
        'active_nav': 'proveedores',
        'registros': registros,
        'q': consulta,
    })


@login_required(login_url='login')
def proveedor_crear(request):
    form = ProveedorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        proveedor = form.save()
        messages.success(request, f'Proveedor “{proveedor.nombre}” creado.')
        return redirect('proveedores')
    return _render_form(request, form, 'Nuevo proveedor', 'proveedores', 'proveedores')


@login_required(login_url='login')
def proveedor_editar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    form = ProveedorForm(request.POST or None, instance=proveedor)
    if request.method == 'POST' and form.is_valid():
        proveedor = form.save()
        messages.success(request, f'Proveedor “{proveedor.nombre}” actualizado.')
        return redirect('proveedores')
    return _render_form(request, form, 'Editar proveedor', 'proveedores', 'proveedores')


@login_required(login_url='login')
def proveedor_eliminar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        nombre = proveedor.nombre
        proveedor.delete()
        messages.success(request, f'Proveedor “{nombre}” eliminado.')
        return redirect('proveedores')
    return _render_confirm(request, proveedor, 'proveedor', 'proveedores', 'proveedores')


@login_required(login_url='login')
def movimientos(request):
    consulta = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    registros = MovimientoInventario.objects.select_related('producto')
    if consulta:
        registros = registros.filter(producto__nombre__icontains=consulta)
    if tipo in {'ENTRADA', 'SALIDA'}:
        registros = registros.filter(tipo=tipo)
    pagina = Paginator(registros.order_by('-fecha'), 15).get_page(
        request.GET.get('page')
    )
    return render(request, 'inventario/movimientos.html', {
        'active_nav': 'movimientos',
        'pagina': pagina,
        'q': consulta,
        'tipo': tipo,
        'entradas': registros.filter(tipo='ENTRADA').aggregate(total=Sum('cantidad'))['total'] or 0,
        'salidas': registros.filter(tipo='SALIDA').aggregate(total=Sum('cantidad'))['total'] or 0,
    })


@login_required(login_url='login')
def movimiento_crear(request):
    form = MovimientoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(
                pk=form.cleaned_data['producto'].pk
            )
            tipo = form.cleaned_data['tipo']
            cantidad = form.cleaned_data['cantidad']
            if tipo == 'SALIDA' and cantidad > producto.stock:
                form.add_error(
                    'cantidad',
                    f'No hay stock suficiente. Disponible: {producto.stock} unidades.',
                )
            else:
                producto.stock = (
                    producto.stock + cantidad
                    if tipo == 'ENTRADA'
                    else producto.stock - cantidad
                )
                producto.save(update_fields=['stock'])
                movimiento = form.save(commit=False)
                movimiento.producto = producto
                movimiento.save()
                messages.success(
                    request,
                    f'{movimiento.get_tipo_display()} registrada correctamente.',
                )
                return redirect('movimientos')
    return _render_form(request, form, 'Nuevo movimiento', 'movimientos', 'movimientos')


@login_required(login_url='login')
def administracion(request):
    return render(request, 'inventario/administracion.html', {
        'active_nav': 'administracion',
        'total_productos': Producto.objects.count(),
        'total_categorias': Categoria.objects.count(),
        'total_proveedores': Proveedor.objects.count(),
        'total_movimientos': MovimientoInventario.objects.count(),
    })


def _render_form(request, form, titulo, active_nav, cancel_url):
    return render(request, 'inventario/formulario.html', {
        'form': form,
        'titulo': titulo,
        'active_nav': active_nav,
        'cancel_url': cancel_url,
    })


def _render_confirm(request, objeto, tipo, active_nav, cancel_url):
    return render(request, 'inventario/confirmar_eliminar.html', {
        'objeto': objeto,
        'tipo': tipo,
        'active_nav': active_nav,
        'cancel_url': cancel_url,
    })

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
    Permite registrar movimientos y actualiza automáticamente
    el stock del producto.
    """

    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        producto = serializer.validated_data['producto']
        tipo = serializer.validated_data['tipo']
        cantidad = serializer.validated_data['cantidad']

        # Bloqueamos el producto durante la operación para evitar
        # inconsistencias si se registran movimientos simultáneamente.
        producto = Producto.objects.select_for_update().get(
            pk=producto.pk
        )

        # Una salida nunca puede superar el stock disponible.
        if tipo == 'SALIDA' and cantidad > producto.stock:
            return Response(
                {
                    'error': (
                        f'No hay stock suficiente. '
                        f'Stock disponible: {producto.stock} unidades.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Actualizar stock.
        if tipo == 'ENTRADA':
            producto.stock += cantidad
        elif tipo == 'SALIDA':
            producto.stock -= cantidad

        producto.save(update_fields=['stock'])

        # Registrar el movimiento.
        movimiento = serializer.save()

        return Response(
            self.get_serializer(movimiento).data,
            status=status.HTTP_201_CREATED
        )

    def get_view_name(self):
        return 'Movimientos de inventario'
