from django.contrib import admin
from django.urls import path, include
from inventario import views


admin.site.site_header = 'Inventario Central · CEIA La Pintana'
admin.site.site_title = 'Administración Inventario Central'
admin.site.index_title = 'Panel de administración del inventario institucional'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('productos/', views.productos, name='productos'),
    path('productos/nuevo/', views.producto_crear, name='producto_crear'),
    path('productos/<int:pk>/editar/', views.producto_editar, name='producto_editar'),
    path('productos/<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    path('categorias/', views.categorias, name='categorias'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
    path('proveedores/', views.proveedores, name='proveedores'),
    path('proveedores/nuevo/', views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/<int:pk>/editar/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_eliminar, name='proveedor_eliminar'),
    path('movimientos/', views.movimientos, name='movimientos'),
    path('movimientos/nuevo/', views.movimiento_crear, name='movimiento_crear'),
    path('administracion/', views.administracion, name='administracion'),
    path('admin/', admin.site.urls),
    path('api/', include('inventario.urls')),
]
