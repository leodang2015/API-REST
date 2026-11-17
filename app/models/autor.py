from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.libro import Libro


class Autor(Base):
    __tablename__ = "autores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nacionalidad: Mapped[str | None] = mapped_column(String(60))
    anio_nacimiento: Mapped[int | None] = mapped_column(Integer)

    libros: Mapped[list["Libro"]] = relationship(back_populates="autor")
