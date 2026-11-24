# Biblioteca API

API REST construida con FastAPI y SQLAlchemy. La base de datos se ejecuta directamente en PostgreSQL local; este proyecto ya no usa Docker.

## Requisitos

- Python 3.11 o posterior
- PostgreSQL 16 o posterior
- Node.js para el frontend Vue

## Configurar PostgreSQL en Windows

Instala PostgreSQL con el instalador oficial y asegúrate de que `psql` esté disponible en `PATH`. Durante la instalación, recuerda la contraseña del usuario administrador `postgres`.

Desde PowerShell, en la raíz del proyecto:

```powershell
Copy-Item .env.example .env
$env:PGPASSWORD = "tu-password-de-postgres"
.\setup-local-postgres.ps1
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

El script crea el rol y la base de datos `biblioteca`, y requiere acceso al usuario administrador de PostgreSQL. Puedes cambiar el puerto, usuario o contraseñas con los parámetros:

```powershell
.\setup-local-postgres.ps1 -HostName localhost -Port 5432 -SuperUser postgres -AppPassword biblioteca
```

Si cambias `AppPassword`, actualiza `DATABASE_URL` en `.env`.

Verifica la API en `http://127.0.0.1:8000/api/v1/health`.

## Frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Consulta la [guía de uso](./GUIA_USO.md) para probar la demostración, crear cuentas y conocer las
funciones de cada rol.
