# Inventario Central · CEIA La Pintana

Aplicación web institucional para administrar productos, categorías, proveedores y
movimientos de stock. El proyecto utiliza Django y Django REST Framework, e incluye
un prototipo web responsive con la identidad visual verde y amarilla del CEIA.

## Ejecución local

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/`. El acceso requiere un usuario de Django. Si no
existe uno, se puede crear con `python manage.py createsuperuser`.

## Rutas principales

- `/`: panel de control.
- `/productos/`, `/categorias/`, `/proveedores/` y `/movimientos/`: gestión web.
- `/administracion/`: accesos administrativos.
- `/api/`: API REST navegable.
- `/admin/`: administración avanzada de Django.
