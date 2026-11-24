# Biblioteca Vue

Frontend Vue 3 + Vite con vistas separadas para bibliotecarios y clientes.

## Iniciar

Desde esta carpeta:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

La API debe estar activa en `http://127.0.0.1:8000`. Vite reenvía `/api` a esa dirección para
evitar problemas CORS durante el desarrollo. Puedes cambiar el destino en `.env` con
`VITE_API_PROXY_TARGET`. La base de datos debe estar actualizada con
`python -m alembic upgrade head`.

Inicia sesión con una cuenta de rol `bibliotecario` para gestionar autores, libros, categorías,
productos, socios, préstamos y usuarios. El bibliotecario también revisa las solicitudes, las acepta
o rechaza y comunica una fecha estimada de entrega.

El registro público crea cuentas de rol `cliente` vinculadas automáticamente a una ficha de socio.
Los clientes pueden consultar el catálogo, solicitar libros y ver el estado y la fecha estimada de
entrega de sus solicitudes. Aceptar una solicitud no registra por sí solo un préstamo.

En la pantalla de acceso, los botones **Bibliotecario** y **Usuario** abren una demostración de solo
lectura con datos de ejemplo. Ningún cambio realizado desde el inicio rápido se guarda; para
persistir cambios hay que iniciar sesión con una cuenta real.
