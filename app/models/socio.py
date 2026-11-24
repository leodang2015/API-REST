from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.prestamo import Prestamo


class Socio(Base):
    __tablename__ = "socios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(30))
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="SET NULL"), unique=True
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    prestamos: Mapped[list["Prestamo"]] = relationship(back_populates="socio")
