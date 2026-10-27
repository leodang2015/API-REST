import argparse
import getpass

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.usuario import Usuario


def main() -> None:
    parser = argparse.ArgumentParser(description="Crear o promover una cuenta de administrador")
    parser.add_argument("--nombre", required=True, help="Nombre del administrador")
    parser.add_argument("--email", required=True, help="Correo del administrador")
    args = parser.parse_args()
    password = getpass.getpass("Contraseña (mínimo 8 caracteres): ")
    if len(password) < 8:
        parser.error("La contraseña debe tener al menos 8 caracteres")

    with SessionLocal() as db:
        email = args.email.strip().lower()
        user = db.scalar(select(Usuario).where(Usuario.email == email))
        if user is None:
            user = Usuario(
                nombre=args.nombre.strip(),
                email=email,
                password_hash=hash_password(password),
                role="admin",
            )
            db.add(user)
        else:
            user.nombre = args.nombre.strip()
            user.password_hash = hash_password(password)
            user.role = "admin"
            user.is_active = True
            user.failed_login_attempts = 0
            user.locked_until = None
        db.commit()
        print(f"Administrador listo: {email}")


if __name__ == "__main__":
    main()
