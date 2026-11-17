def limpiar_nombre(valor: str | None, *, capitalizar: bool = False) -> str | None:
    if valor is None:
        return None
    nombre = " ".join(valor.split())
    return nombre.capitalize() if capitalizar else nombre
