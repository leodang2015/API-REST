from typing import BinaryIO

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.controllers.common import guardar
from app.models.autor import Autor
from app.models.categoria import Categoria
from app.models.libro import Libro
from app.models.prestamo import Prestamo
from app.schemas.libro import LibroActualizar, LibroCrear
from app.services.cloudinary import subir_portada


def _consulta_base():
    return select(Libro).options(selectinload(Libro.autor), selectinload(Libro.categorias))


def listar(
    db: Session,
    autor_id: int | None = None,
    categoria_id: int | None = None,
    buscar: str | None = None,
) -> list[Libro]:
    consulta = _consulta_base()
    if autor_id is not None:
        consulta = consulta.where(Libro.autor_id == autor_id)
    if categoria_id is not None:
        consulta = consulta.join(Libro.categorias).where(Categoria.id == categoria_id)
    if buscar:
        consulta = consulta.where(Libro.titulo.ilike(f"%{buscar}%"))
    return list(db.scalars(consulta.order_by(Libro.titulo)).unique())


def obtener(db: Session, libro_id: int) -> Libro:
    libro = db.scalar(_consulta_base().where(Libro.id == libro_id))
    if libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    return libro


def _validar_isbn_unico(db: Session, isbn: str, excluir_id: int | None = None) -> None:
    consulta = select(Libro.id).where(func.lower(Libro.isbn) == isbn.lower())
    if excluir_id is not None:
        consulta = consulta.where(Libro.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe el libro con ISBN '{isbn}'",
        )


def _obtener_categorias(db: Session, categoria_ids: list[int]) -> list[Categoria]:
    ids_unicos = set(categoria_ids)
    categorias = list(db.scalars(select(Categoria).where(Categoria.id.in_(ids_unicos))))
    if len(categorias) != len(ids_unicos):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Una de las categorías no existe",
        )
    return categorias


def crear(
    db: Session,
    datos: LibroCrear,
    archivo_portada: BinaryIO,
    nombre_original: str,
) -> Libro:
    autor = db.get(Autor, datos.autor_id)
    if autor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor no encontrado")
    if datos.disponible > datos.ejemplares:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Los ejemplares disponibles no pueden superar el total",
        )
    categorias = _obtener_categorias(db, datos.categoria_ids)
    _validar_isbn_unico(db, datos.isbn)
    libro = Libro(
        titulo=datos.titulo,
        isbn=datos.isbn,
        descripcion=datos.descripcion,
        anio_publicacion=datos.anio_publicacion,
        ejemplares=datos.ejemplares,
        disponible=datos.disponible,
        autor_id=datos.autor_id,
        categorias=categorias,
    )
    db.add(libro)
    db.flush()
    portada = subir_portada(libro.id, archivo_portada, nombre_original)
    libro.portada_url = str(portada.portada_url)
    libro.portada_public_id = portada.portada_public_id
    guardar(db, f"Ya existe el libro con ISBN '{datos.isbn}'")
    return obtener(db, libro.id)


def actualizar(db: Session, libro_id: int, datos: LibroActualizar) -> Libro:
    libro = obtener(db, libro_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "autor_id" in cambios and db.get(Autor, cambios["autor_id"]) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Autor no encontrado")
    if "categoria_ids" in cambios:
        libro.categorias = _obtener_categorias(db, cambios.pop("categoria_ids"))
    if "isbn" in cambios:
        _validar_isbn_unico(db, cambios["isbn"], excluir_id=libro_id)

    nuevo_total = cambios.get("ejemplares", libro.ejemplares)
    nueva_disponibilidad = cambios.get("disponible", libro.disponible)
    prestamos_activos = db.scalar(
        select(func.count(Prestamo.id)).where(
            Prestamo.libro_id == libro_id,
            Prestamo.devuelto.is_(False),
        )
    ) or 0
    if nueva_disponibilidad > nuevo_total or nueva_disponibilidad + prestamos_activos > nuevo_total:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El total de ejemplares no puede ser menor que los disponibles y prestados",
        )
    for campo, valor in cambios.items():
        setattr(libro, campo, valor)
    guardar(db, "Ya existe otro libro con ese ISBN")
    return obtener(db, libro_id)


def eliminar(db: Session, libro_id: int) -> None:
    libro = obtener(db, libro_id)
    total_prestamos = db.scalar(
        select(func.count(Prestamo.id)).where(Prestamo.libro_id == libro_id)
    ) or 0
    if total_prestamos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El libro tiene {total_prestamos} préstamo(s); no se puede eliminar",
        )
    db.delete(libro)
    guardar(db, "No se puede eliminar el libro")
