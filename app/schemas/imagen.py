from pydantic import AnyHttpUrl, Field

from app.schemas.pagina import ORMModel


class PortadaRespuesta(ORMModel):
    libro_id: int = Field(gt=0)
    portada_url: AnyHttpUrl
    portada_public_id: str = Field(min_length=1)
    formato: str = Field(min_length=1, max_length=20)
    ancho: int = Field(gt=0)
    alto: int = Field(gt=0)
    bytes: int = Field(gt=0)
    nombre_original: str = Field(min_length=1, max_length=255)
    miniatura_url: AnyHttpUrl
