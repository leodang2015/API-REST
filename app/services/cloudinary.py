from typing import Any, BinaryIO, TypedDict
from urllib.parse import unquote, urlsplit

import cloudinary
import cloudinary.api
import cloudinary.uploader
from cloudinary import CloudinaryImage
from cloudinary.utils import cloudinary_url

from app.core.config import settings
from app.schemas.imagen import PortadaRespuesta


class ImagenCloudinary(TypedDict):
    public_id: str
    secure_url: str
    width: int
    height: int
    format: str
    bytes: int


def _configurar_cloudinary() -> None:
    if settings.cloudinary_url:
        parsed_url = urlsplit(settings.cloudinary_url.get_secret_value())
        if (
            parsed_url.scheme != "cloudinary"
            or not parsed_url.hostname
            or not parsed_url.username
            or not parsed_url.password
        ):
            raise RuntimeError(
                "CLOUDINARY_URL debe tener el formato "
                "cloudinary://<api_key>:<api_secret>@<cloud_name>"
            )
        cloudinary.config(
            cloud_name=parsed_url.hostname,
            api_key=unquote(parsed_url.username),
            api_secret=unquote(parsed_url.password),
            secure=True,
        )
        return

    if not all(
        (
            settings.cloudinary_cloud_name,
            settings.cloudinary_api_key,
            settings.cloudinary_api_secret,
        )
    ):
        raise RuntimeError(
            "Configura CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY y "
            "CLOUDINARY_API_SECRET en el archivo .env"
        )

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret.get_secret_value(),
        secure=True,
    )


def obtener_detalles_imagen(public_id: str) -> dict[str, Any]:
    _configurar_cloudinary()
    return cloudinary.api.resource(public_id, resource_type="image")


def etiquetar_por_ancho(public_id: str) -> str:
    detalles = obtener_detalles_imagen(public_id)
    ancho = detalles.get("width", 0)
    if not isinstance(ancho, int):
        raise ValueError("Cloudinary devolvió un ancho de imagen inválido")

    etiqueta = "large" if ancho > 900 else "medium" if ancho > 500 else "small"
    cloudinary.api.update(
        public_id,
        tags=[etiqueta],
        resource_type="image",
    )
    return etiqueta


def url_transformada(
    public_id: str,
    *,
    ancho: int = 100,
    alto: int = 150,
) -> str:
    if ancho <= 0 or alto <= 0:
        raise ValueError("El ancho y el alto deben ser mayores que cero")
    _configurar_cloudinary()
    return CloudinaryImage(public_id).build_url(
        width=ancho,
        height=alto,
        crop="fill",
        secure=True,
    )


def subir_imagen(
    archivo: BinaryIO,
    *,
    carpeta: str = "biblioteca/portadas",
    public_id: str | None = None,
    sobrescribir: bool = False,
) -> ImagenCloudinary:
    _configurar_cloudinary()
    options: dict[str, str | bool] = {
        "folder": carpeta,
        "resource_type": "image",
        "overwrite": sobrescribir,
        "invalidate": sobrescribir,
    }
    if public_id is not None:
        options["public_id"] = public_id

    resultado = cloudinary.uploader.upload(archivo, **options)
    return {
        "public_id": resultado["public_id"],
        "secure_url": resultado["secure_url"],
        "width": resultado["width"],
        "height": resultado["height"],
        "format": resultado["format"],
        "bytes": resultado["bytes"],
    }


def subir_portada(
    libro_id: int,
    archivo: BinaryIO,
    nombre_original: str,
) -> PortadaRespuesta:
    if libro_id <= 0:
        raise ValueError("El ID del libro debe ser mayor que cero")
    if not nombre_original.strip():
        raise ValueError("El archivo de portada debe tener nombre")

    imagen = subir_imagen(
        archivo,
        carpeta="biblioteca/portadas",
        public_id=f"libro_{libro_id}",
        sobrescribir=True,
    )
    return PortadaRespuesta(
        libro_id=libro_id,
        portada_url=imagen["secure_url"],
        portada_public_id=imagen["public_id"],
        formato=imagen["format"],
        ancho=imagen["width"],
        alto=imagen["height"],
        bytes=imagen["bytes"],
        nombre_original=nombre_original,
        miniatura_url=url_miniatura(imagen["public_id"], ancho=200, alto=300),
    )


def eliminar_imagen(public_id: str) -> bool:
    _configurar_cloudinary()
    resultado = cloudinary.uploader.destroy(
        public_id,
        resource_type="image",
        invalidate=True,
    )
    if resultado.get("result") == "ok":
        return True
    if resultado.get("result") == "not found":
        return False
    raise RuntimeError(f"Cloudinary no pudo eliminar la imagen: {resultado.get('result')}")


def url_miniatura(public_id: str, *, ancho: int = 200, alto: int = 300) -> str:
    _configurar_cloudinary()
    url, _ = cloudinary_url(
        public_id,
        width=ancho,
        height=alto,
        crop="fill",
        fetch_format="auto",
        quality="auto",
        secure=True,
    )
    return url
