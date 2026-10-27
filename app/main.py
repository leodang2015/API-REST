from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import CuentaBloqueada, NoAutenticado, Prohibido
from app.routes import auth, health, usuario

app = FastAPI(title=settings.app_name)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(NoAutenticado)
async def no_autenticado_handler(request: Request, exc: NoAutenticado) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": exc.detail},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(Prohibido)
async def prohibido_handler(request: Request, exc: Prohibido) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.detail})


@app.exception_handler(CuentaBloqueada)
async def cuenta_bloqueada_handler(request: Request, exc: CuentaBloqueada) -> JSONResponse:
    return JSONResponse(status_code=423, content={"detail": exc.detail})


app.include_router(auth.router, prefix="/api/v1")
app.include_router(usuario.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")