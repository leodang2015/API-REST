from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.libro import Libro
    from app.models.socio import Socio


class SolicitudPrestamo(Base):
    __tablename__ = "solicitudes_prestamo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    socio_id: Mapped[int] = mapped_column(
        ForeignKey("socios.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    fecha_entrega_estimada: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    socio: Mapped["Socio"] = relationship()
    libro: Mapped["Libro"] = relationship()
