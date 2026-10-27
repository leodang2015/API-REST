class NoAutenticado(Exception):
    def __init__(self, detail: str = "No autenticado") -> None:
        self.detail = detail
        super().__init__(detail)


class Prohibido(Exception):
    def __init__(self, detail: str = "No tienes permiso para realizar esta acción") -> None:
        self.detail = detail
        super().__init__(detail)


class CuentaBloqueada(Exception):
    def __init__(self, detail: str = "La cuenta está bloqueada temporalmente") -> None:
        self.detail = detail
        super().__init__(detail)