# Guía de uso de la Biblioteca

## Iniciar la aplicación

Antes de arrancar, confirma que `DATABASE_URL` en `.env` apunta a la base de datos que quieres
utilizar. No compartas ese archivo ni publiques la contraseña.

En una terminal de PowerShell, desde la raíz del proyecto:

```powershell
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

En otra terminal, inicia el frontend:

```powershell
cd frontend
npm run dev
```

Abre la dirección que muestra Vite, normalmente `http://localhost:5173`. La API está disponible en
`http://127.0.0.1:8000`; su documentación interactiva está en `http://127.0.0.1:8000/docs`.

> Ejecuta la migración solo después de comprobar el destino de `DATABASE_URL`. Esta operación
> actualiza la base de datos seleccionada.

## Inicio rápido: demostración

En la pantalla de acceso aparecen los botones **Bibliotecario** y **Usuario**. Abren el sistema con
datos ficticios para explorar las vistas. La demostración no crea cuentas, no guarda cambios y no
envía operaciones de escritura a la API.

Para terminarla, pulsa **Salir de demostración** en el menú lateral. Volverás a la pantalla de
acceso. Al recargar la página también termina la demostración.

## Usar una cuenta real

### Cuenta de usuario

1. En la pantalla de acceso, selecciona **Regístrate**.
2. Completa nombre, correo y contraseña.
3. Inicia sesión con la cuenta creada.

El registro público crea una cuenta con rol `cliente` y la vincula automáticamente a una ficha de
socio. Las operaciones de esta cuenta se guardan en la base de datos configurada.

### Cuenta de bibliotecario

El rol de bibliotecario se crea o asigna desde la consola, no desde el registro público. Desde la
raíz del proyecto, con `.env` apuntando a la base de datos deseada, ejecuta:

```powershell
python -m app.scripts.crear_admin --nombre "Nombre del bibliotecario" --email "correo@ejemplo.com"
```

El comando solicita la contraseña sin mostrarla. Si el correo ya pertenece a una cuenta, la promueve
a bibliotecario y actualiza su contraseña.

## Funciones por rol

### Cliente

- Consulta los libros del catálogo.
- Solicita un libro y revisa el estado de la solicitud.
- Puede cancelar una solicitud mientras siga pendiente.
- Cuando el bibliotecario la acepta, consulta la fecha estimada de entrega.

### Bibliotecario

- Administra autores, libros, categorías, productos, socios, préstamos y usuarios.
- Revisa solicitudes de los clientes y puede aceptarlas o rechazarlas.
- Al aceptar, debe indicar una fecha estimada de entrega.
- La aceptación de una solicitud **no registra automáticamente un préstamo**. El préstamo se
  registra aparte desde la sección **Préstamos**.

## Salir

- En el modo de demostración, usa **Salir de demostración**.
- Con una cuenta real, usa **Cerrar sesión** en el menú lateral.
