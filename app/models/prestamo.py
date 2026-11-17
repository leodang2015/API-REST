from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.libro import Libro
    from app.models.socio import Socio


class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    socio_id: Mapped[int] = mapped_column(
        ForeignKey("socios.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    libro_id: Mapped[int] = mapped_column(
        ForeignKey("libros.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    fecha_prestamo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    fecha_limite: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_devolucion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    multa: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False), default=0, nullable=False)
    devuelto: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    socio: Mapped["Socio"] = relationship(back_populates="prestamos")
    libro: Mapped["Libro"] = relationship(back_populates="prestamos")
