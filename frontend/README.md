# Biblioteca Vue

Frontend Vue 3 + Vite para iniciar sesión y registrar libros con una portada binaria.

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

Inicia sesión con una cuenta administradora. El formulario envía los campos del libro y
`archivo_portada` como `multipart/form-data`; el backend carga la imagen en Cloudinary y devuelve
la URL guardada.
