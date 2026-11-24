from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile, status

from app.core.dependencies import SessionDep, requiere_rol
from app.core.uploads import validar_archivo_portada
from app.models.libro import Libro
from app.models.usuario import Usuario
from app.schemas.imagen import PortadaRespuesta
from app.services.cloudinary import subir_portada as subir_portada_cloudinary

router = APIRouter(prefix="/libros", tags=["portadas"])
AdminDep = Annotated[Usuario, Depends(requiere_rol("bibliotecario"))]


@router.post(
    "/{libro_id}/portada",
    response_model=PortadaRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def cargar_portada(
    libro_id: Annotated[int, Path(gt=0)],
    archivo: Annotated[UploadFile, File()],
    db: SessionDep,
    _admin: AdminDep,
) -> PortadaRespuesta:
    libro = db.get(Libro, libro_id)
    if libro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Libro no encontrado",
        )

    nombre_original = validar_archivo_portada(archivo)

    portada = subir_portada_cloudinary(libro_id, archivo.file, nombre_original)
    libro.portada_url = str(portada.portada_url)
    libro.portada_public_id = portada.portada_public_id
    db.commit()
    return portada
