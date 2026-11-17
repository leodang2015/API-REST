"""Agregar autores, categorías, libros, socios, préstamos y productos."""

from alembic import op
import sqlalchemy as sa

revision = "0002_library_domain"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "autores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("nacionalidad", sa.String(length=60), nullable=True),
        sa.Column("anio_nacimiento", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_autores"),
        sa.UniqueConstraint("nombre", name="uq_autores_nombre"),
    )

    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_categorias"),
        sa.UniqueConstraint("nombre", name="uq_categorias_nombre"),
    )

    op.create_table(
        "socios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_socios"),
        sa.UniqueConstraint("email", name="uq_socios_email"),
    )
    op.create_index("ix_socios_nombre", "socios", ["nombre"], unique=False)

    op.create_table(
        "libros",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=150), nullable=False),
        sa.Column("isbn", sa.String(length=20), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=True),
        sa.Column("anio_publicacion", sa.Integer(), nullable=True),
        sa.Column("ejemplares", sa.Integer(), nullable=False),
        sa.Column("disponible", sa.Integer(), nullable=False),
        sa.Column("portada_url", sa.String(length=2048), nullable=True),
        sa.Column("portada_public_id", sa.String(length=255), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["autor_id"], ["autores.id"], name="fk_libros_autor_id_autores", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_libros"),
        sa.UniqueConstraint("isbn", name="uq_libros_isbn"),
    )
    op.create_index("ix_libros_autor_id", "libros", ["autor_id"], unique=False)
    op.create_index("ix_libros_titulo", "libros", ["titulo"], unique=False)
    op.create_table(
        "libro_categoria",
        sa.Column("libro_id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], name="fk_libro_categoria_categoria_id_categorias", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["libro_id"], ["libros.id"], name="fk_libro_categoria_libro_id_libros", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("libro_id", "categoria_id", name="pk_libro_categoria"),
    )

    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=300), nullable=True),
        sa.Column("precio", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], name="fk_productos_categoria_id_categorias", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_productos"),
        sa.UniqueConstraint("nombre", name="uq_productos_nombre"),
    )
    op.create_index("ix_productos_categoria_id", "productos", ["categoria_id"], unique=False)

    op.create_table(
        "prestamos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("socio_id", sa.Integer(), nullable=False),
        sa.Column("libro_id", sa.Integer(), nullable=False),
        sa.Column("fecha_prestamo", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("fecha_limite", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_devolucion", sa.DateTime(timezone=True), nullable=True),
        sa.Column("multa", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("devuelto", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["libro_id"], ["libros.id"], name="fk_prestamos_libro_id_libros", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["socio_id"], ["socios.id"], name="fk_prestamos_socio_id_socios", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_prestamos"),
    )
    op.create_index("ix_prestamos_libro_id", "prestamos", ["libro_id"], unique=False)
    op.create_index("ix_prestamos_socio_id", "prestamos", ["socio_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_prestamos_socio_id", table_name="prestamos")
    op.drop_index("ix_prestamos_libro_id", table_name="prestamos")
    op.drop_table("prestamos")
    op.drop_index("ix_productos_categoria_id", table_name="productos")
    op.drop_table("productos")
    op.drop_table("libro_categoria")
    op.drop_index("ix_libros_titulo", table_name="libros")
    op.drop_index("ix_libros_autor_id", table_name="libros")
    op.drop_table("libros")
    op.drop_index("ix_socios_nombre", table_name="socios")
    op.drop_table("socios")
    op.drop_table("categorias")
    op.drop_table("autores")
