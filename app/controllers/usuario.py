from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import Prohibido
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioActualizar


def listar_usuarios(db: Session, offset: int, limit: int) -> tuple[list[Usuario], int]:
    items = list(db.scalars(select(Usuario).order_by(Usuario.id).offset(offset).limit(limit)).all())
    total = db.scalar(select(func.count()).select_from(Usuario)) or 0
    return items, total


def obtener_usuario(db: Session, user_id: int) -> Usuario | None:
    return db.get(Usuario, user_id)


def actualizar_usuario(db: Session, user: Usuario, data: UsuarioActualizar) -> Usuario:
    changes = data.model_dump(exclude_unset=True)
    if "email" in changes and changes["email"] is not None:
        email = str(changes["email"]).lower()
        existing = db.scalar(select(Usuario).where(Usuario.email == email, Usuario.id != user.id))
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una cuenta con ese correo",
            )
        changes["email"] = email
    for field, value in changes.items():
        if value is not None:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def desactivar_usuario(db: Session, user: Usuario) -> None:
    if user.role == "admin":
        raise Prohibido("No se puede desactivar una cuenta de administrador desde esta ruta")
    user.is_active = False
    db.commit()
