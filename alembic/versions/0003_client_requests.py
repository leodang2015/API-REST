"""Agregar roles bibliotecario/cliente y solicitudes de préstamo."""

from alembic import op
import sqlalchemy as sa

revision = "0003_client_requests"
down_revision = "0002_library_domain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("socios", sa.Column("usuario_id", sa.Integer(), nullable=True))
    op.alter_column(
        "socios",
        "email",
        existing_type=sa.String(length=120),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "fk_socios_usuario_id_usuarios",
        "socios",
        "usuarios",
        ["usuario_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_unique_constraint("uq_socios_usuario_id", "socios", ["usuario_id"])

    op.execute("UPDATE usuarios SET role = 'bibliotecario' WHERE role = 'admin'")
    op.execute("UPDATE usuarios SET role = 'cliente' WHERE role = 'user'")
    op.execute(
        """
        UPDATE socios
        SET usuario_id = usuarios.id
        FROM usuarios
        WHERE lower(socios.email) = lower(usuarios.email)
          AND usuarios.role = 'cliente'
          AND socios.usuario_id IS NULL
        """
    )
    op.execute(
        """
        INSERT INTO socios (nombre, email, activo, creado_en, usuario_id)
        SELECT usuarios.nombre, usuarios.email, usuarios.is_active,
               CURRENT_TIMESTAMP, usuarios.id
        FROM usuarios
        WHERE usuarios.role = 'cliente'
          AND NOT EXISTS (
              SELECT 1 FROM socios
              WHERE lower(socios.email) = lower(usuarios.email)
          )
        """
    )

    op.create_table(
        "solicitudes_prestamo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("socio_id", sa.Integer(), nullable=False),
        sa.Column("libro_id", sa.Integer(), nullable=False),
        sa.Column(
            "fecha_solicitud",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "estado",
            sa.String(length=20),
            server_default="pendiente",
            nullable=False,
        ),
        sa.Column("fecha_entrega_estimada", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["libro_id"],
            ["libros.id"],
            name="fk_solicitudes_prestamo_libro_id_libros",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["socio_id"],
            ["socios.id"],
            name="fk_solicitudes_prestamo_socio_id_socios",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_solicitudes_prestamo"),
    )
    op.create_index(
        "ix_solicitudes_prestamo_libro_id",
        "solicitudes_prestamo",
        ["libro_id"],
        unique=False,
    )
    op.create_index(
        "ix_solicitudes_prestamo_socio_id",
        "solicitudes_prestamo",
        ["socio_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_solicitudes_prestamo_socio_id", table_name="solicitudes_prestamo")
    op.drop_index("ix_solicitudes_prestamo_libro_id", table_name="solicitudes_prestamo")
    op.drop_table("solicitudes_prestamo")
    op.execute("UPDATE usuarios SET role = 'admin' WHERE role = 'bibliotecario'")
    op.execute("UPDATE usuarios SET role = 'user' WHERE role = 'cliente'")
    op.drop_constraint("uq_socios_usuario_id", "socios", type_="unique")
    op.drop_constraint("fk_socios_usuario_id_usuarios", "socios", type_="foreignkey")
    op.drop_column("socios", "usuario_id")
