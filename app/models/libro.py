from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.autor import Autor
    from app.models.categoria import Categoria
    from app.models.prestamo import Prestamo


libro_categoria = Table(
    "libro_categoria",
    Base.metadata,
    Column("libro_id", ForeignKey("libros.id", ondelete="CASCADE"), primary_key=True),
    Column("categoria_id", ForeignKey("categorias.id", ondelete="CASCADE"), primary_key=True),
)


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(500))
    anio_publicacion: Mapped[int | None] = mapped_column(Integer)
    ejemplares: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    disponible: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    portada_url: Mapped[str | None] = mapped_column(String(2048))
    portada_public_id: Mapped[str | None] = mapped_column(String(255))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    autor_id: Mapped[int] = mapped_column(
        ForeignKey("autores.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    autor: Mapped["Autor"] = relationship(back_populates="libros")
    categorias: Mapped[list["Categoria"]] = relationship(
        secondary=libro_categoria,
        back_populates="libros",
    )
    prestamos: Mapped[list["Prestamo"]] = relationship(back_populates="libro")
