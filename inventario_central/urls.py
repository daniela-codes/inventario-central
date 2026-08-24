from django.contrib import admin
from django.urls import path, include
from inventario.views import home


admin.site.site_header = 'Inventario Central · CEIA La Pintana'
admin.site.site_title = 'Administración Inventario Central'
admin.site.index_title = 'Panel de administración del inventario institucional'

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('inventario.urls')),
]