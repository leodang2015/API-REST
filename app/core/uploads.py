from fastapi import HTTPException, UploadFile, status


TIPOS_IMAGEN_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}


def validar_archivo_portada(archivo: UploadFile) -> str:
    if archivo.content_type not in TIPOS_IMAGEN_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El archivo debe ser una imagen JPEG, PNG o WebP",
        )

    nombre = (archivo.filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    if not nombre or len(nombre) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del archivo debe tener entre 1 y 255 caracteres",
        )
    return nombre
