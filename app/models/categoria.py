from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.libro import Libro
    from app.models.producto import Producto


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(200))

    libros: Mapped[list["Libro"]] = relationship(
        secondary="libro_categoria",
        back_populates="categorias",
    )
    productos: Mapped[list["Producto"]] = relationship(back_populates="categoria")
