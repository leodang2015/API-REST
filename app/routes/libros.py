from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status

from app.controllers import libros as controlador
from app.core.dependencies import CurrentUser, SessionDep, requiere_rol
from app.core.uploads import validar_archivo_portada
from app.models.usuario import Usuario
from app.schemas.libro import LibroActualizar, LibroCrear, LibroLeer

router = APIRouter(prefix="/libros", tags=["libros"])
AdminDep = Annotated[Usuario, Depends(requiere_rol("bibliotecario"))]


@router.get("", response_model=list[LibroLeer])
def listar(
    _user: CurrentUser,
    db: SessionDep,
    autor_id: int | None = Query(default=None, gt=0),
    categoria_id: int | None = Query(default=None, gt=0),
    buscar: str | None = Query(default=None, max_length=150),
) -> list[LibroLeer]:
    return controlador.listar(db, autor_id=autor_id, categoria_id=categoria_id, buscar=buscar)


@router.get("/{libro_id}", response_model=LibroLeer)
def obtener(libro_id: int, _user: CurrentUser, db: SessionDep) -> LibroLeer:
    return controlador.obtener(db, libro_id)


@router.post("", response_model=LibroLeer, status_code=status.HTTP_201_CREATED)
def crear(
    titulo: Annotated[str, Form(min_length=2, max_length=150)],
    isbn: Annotated[str, Form(min_length=8, max_length=20)],
    autor_id: Annotated[int, Form(gt=0)],
    archivo_portada: Annotated[UploadFile, File()],
    db: SessionDep,
    _admin: AdminDep,
    descripcion: Annotated[str | None, Form(max_length=500)] = None,
    anio_publicacion: Annotated[int | None, Form(ge=1000)] = None,
    ejemplares: Annotated[int, Form(ge=1)] = 1,
    disponible: Annotated[int, Form(ge=0)] = 1,
    categoria_ids: Annotated[list[int] | None, Form()] = None,
) -> LibroLeer:
    datos = LibroCrear(
        titulo=titulo,
        isbn=isbn,
        descripcion=descripcion,
        anio_publicacion=anio_publicacion,
        ejemplares=ejemplares,
        disponible=disponible,
        autor_id=autor_id,
        categoria_ids=categoria_ids or [],
    )
    nombre_original = validar_archivo_portada(archivo_portada)
    return controlador.crear(
        db,
        datos,
        archivo_portada.file,
        nombre_original,
    )


@router.patch("/{libro_id}", response_model=LibroLeer)
def actualizar(
    libro_id: int,
    datos: LibroActualizar,
    db: SessionDep,
    _admin: AdminDep,
) -> LibroLeer:
    return controlador.actualizar(db, libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(libro_id: int, db: SessionDep, _admin: AdminDep) -> Response:
    controlador.eliminar(db, libro_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
