from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.categoria import Categoria


class Producto(Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(300))
    precio: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    categoria: Mapped["Categoria"] = relationship(back_populates="productos")
