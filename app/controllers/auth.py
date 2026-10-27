from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import CuentaBloqueada, NoAutenticado
from app.core.security import (
    create_token,
    decode_token,
    hash_password,
    token_digest,
    token_expiration,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest
from app.schemas.usuario import UsuarioCrear


def registrar_usuario(db: Session, data: UsuarioCrear) -> Usuario:
    email = str(data.email).lower()
    existing_user = db.scalar(select(Usuario).where(Usuario.email == email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo",
        )

    user = Usuario(nombre=data.nombre, email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def autenticar_usuario(db: Session, data: LoginRequest) -> Usuario:
    user = db.scalar(select(Usuario).where(Usuario.email == str(data.email).lower()))
    if user is None:
        raise NoAutenticado("Correo o contraseña incorrectos")
    if not user.is_active:
        raise NoAutenticado("La cuenta está inactiva")

    now = datetime.now(timezone.utc)
    if user.locked_until is not None:
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=timezone.utc)
        if locked_until > now:
            raise CuentaBloqueada()
        user.locked_until = None
        user.failed_login_attempts = 0

    if not verify_password(data.password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.max_failed_login_attempts:
            user.locked_until = now + timedelta(minutes=settings.account_lock_minutes)
        db.commit()
        if user.locked_until is not None:
            raise CuentaBloqueada()
        raise NoAutenticado("Correo o contraseña incorrectos")

    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    return user


def crear_tokens(db: Session, user: Usuario) -> dict[str, str]:
    access = create_token(
        str(user.id),
        "access",
        timedelta(minutes=settings.access_token_minutes),
    )
    refresh = create_token(
        str(user.id),
        "refresh",
        timedelta(days=settings.refresh_token_days),
    )
    db.add(
        RefreshToken(
            usuario_id=user.id,
            token_hash=token_digest(refresh),
            expires_at=token_expiration(refresh),
        )
    )
    db.commit()
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


def renovar_tokens(db: Session, raw_token: str) -> dict[str, str]:
    try:
        claims = decode_token(raw_token)
        if claims.get("type") != "refresh":
            raise NoAutenticado("Se requiere un token de renovación")
        user_id = int(claims["sub"])
    except (JWTError, KeyError, TypeError, ValueError) as exc:
        raise NoAutenticado("Token de renovación inválido o expirado") from exc

    stored_token = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_digest(raw_token))
    )
    now = datetime.now(timezone.utc)
    if stored_token is None or stored_token.revoked_at is not None:
        raise NoAutenticado("Token de renovación revocado o desconocido")
    expiration = stored_token.expires_at
    if expiration.tzinfo is None:
        expiration = expiration.replace(tzinfo=timezone.utc)
    if expiration <= now or stored_token.usuario_id != user_id:
        raise NoAutenticado("Token de renovación expirado o inválido")

    user = db.get(Usuario, user_id)
    if user is None or not user.is_active:
        raise NoAutenticado("Usuario inexistente o inactivo")

    stored_token.revoked_at = now
    result = crear_tokens(db, user)
    return result


def revocar_refresh_token(db: Session, raw_token: str) -> None:
    stored_token = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == token_digest(raw_token))
    )
    if stored_token is not None and stored_token.revoked_at is None:
        stored_token.revoked_at = datetime.now(timezone.utc)
        db.commit()
