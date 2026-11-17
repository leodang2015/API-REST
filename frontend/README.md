# Biblioteca Vue

Frontend Vue 3 + Vite para iniciar sesión y registrar libros con una portada binaria.

## Iniciar

Desde esta carpeta:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

La API debe estar activa en `http://localhost:8000`. Puedes cambiar su URL en `.env` con
`VITE_API_URL`. El backend debe tener `CORS_ORIGINS=["http://localhost:5173"]` y su base de
datos actualizada con `python -m alembic upgrade head`.

Inicia sesión con una cuenta administradora. El formulario envía los campos del libro y
`archivo_portada` como `multipart/form-data`; el backend carga la imagen en Cloudinary y devuelve
la URL guardada.
