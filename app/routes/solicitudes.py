from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.controllers import solicitudes as controlador
from app.core.dependencies import CurrentUser, SessionDep, requiere_rol
from app.core.exceptions import Prohibido
from app.models.usuario import Usuario
from app.schemas.solicitud_prestamo import SolicitudCrear, SolicitudLeer, SolicitudResolver

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])
BibliotecarioDep = Annotated[Usuario, Depends(requiere_rol("bibliotecario"))]
ClienteDep = Annotated[Usuario, Depends(requiere_rol("cliente"))]


@router.get("", response_model=list[SolicitudLeer])
def listar(current_user: CurrentUser, db: SessionDep) -> list[SolicitudLeer]:
    if current_user.role == "bibliotecario":
        return controlador.listar(db)
    if current_user.role == "cliente":
        return controlador.listar(db, user_id=current_user.id)
    raise Prohibido()


@router.get("/{solicitud_id}", response_model=SolicitudLeer)
def obtener(solicitud_id: int, current_user: CurrentUser, db: SessionDep) -> SolicitudLeer:
    solicitud = controlador.obtener(db, solicitud_id)
    if (
        current_user.role != "bibliotecario"
        and (current_user.role != "cliente" or solicitud.socio.usuario_id != current_user.id)
    ):
        raise Prohibido()
    return solicitud


@router.post("", response_model=SolicitudLeer, status_code=status.HTTP_201_CREATED)
def crear(
    datos: SolicitudCrear,
    db: SessionDep,
    cliente: ClienteDep,
) -> SolicitudLeer:
    return controlador.crear(db, cliente.id, datos)


@router.patch("/{solicitud_id}", response_model=SolicitudLeer)
def resolver(
    solicitud_id: int,
    datos: SolicitudResolver,
    db: SessionDep,
    _bibliotecario: BibliotecarioDep,
) -> SolicitudLeer:
    return controlador.resolver(db, solicitud_id, datos)


@router.delete("/{solicitud_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(
    solicitud_id: int,
    current_user: CurrentUser,
    db: SessionDep,
) -> Response:
    if current_user.role == "bibliotecario":
        controlador.eliminar(db, solicitud_id)
    elif current_user.role == "cliente":
        controlador.cancelar_cliente(db, solicitud_id, current_user.id)
    else:
        raise Prohibido()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
