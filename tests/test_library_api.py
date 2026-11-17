from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.dependencies import get_current_user, get_db
from app.main import app
from app.models.libro import Libro
import app.controllers.libros as libros
import app.routes.portadas as portadas
from app.schemas.imagen import PortadaRespuesta


@pytest.fixture
def api_client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False)
    role = {"value": "admin"}

    def subir_portada(libro_id, archivo, nombre_original):
        return PortadaRespuesta(
            libro_id=libro_id,
            portada_url="https://res.cloudinary.com/demo/image/upload/cover.jpg",
            portada_public_id=f"biblioteca/portadas/libro_{libro_id}",
            formato="jpg",
            ancho=500,
            alto=700,
            bytes=321,
            nombre_original=nombre_original,
            miniatura_url="https://res.cloudinary.com/demo/image/upload/thumbnail.jpg",
        )

    def override_db():
        with test_session() as db:
            yield db

    monkeypatch.setattr(libros, "subir_portada", subir_portada)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(role=role["value"])
    with TestClient(app) as client:
        yield client, role, test_session
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def crear_libro(client: TestClient) -> dict:
    autor = client.post("/api/v1/autores", json={"nombre": "Gabriel García Márquez"})
    assert autor.status_code == 201
    categoria = client.post("/api/v1/categorias", json={"nombre": "novela"})
    assert categoria.status_code == 201
    libro = client.post(
        "/api/v1/libros",
        data={
            "titulo": "Cien años de soledad",
            "isbn": "9781234567890",
            "autor_id": str(autor.json()["id"]),
            "categoria_ids": [categoria.json()["id"]],
        },
        files={"archivo_portada": ("cover.png", b"image-bytes", "image/png")},
    )
    assert libro.status_code == 201
    return {"autor": autor.json(), "categoria": categoria.json(), "libro": libro.json()}


def test_catalog_product_and_loan_workflow(api_client):
    client, _, _ = api_client
    records = crear_libro(client)

    product = client.post(
        "/api/v1/productos",
        json={
            "nombre": "Separador de libros",
            "precio": 2.5,
            "categoria_id": records["categoria"]["id"],
        },
    )
    assert product.status_code == 201, product.text
    assert product.json()["categoria"]["nombre"] == "Novela"
    products = client.get(f"/api/v1/categorias/{records['categoria']['id']}/productos")
    assert products.status_code == 200 and len(products.json()) == 1

    socio = client.post(
        "/api/v1/socios",
        json={"nombre": "Ana Pérez", "email": "ana@example.com"},
    )
    assert socio.status_code == 201, socio.text
    prestamo = client.post(
        "/api/v1/prestamos",
        json={
            "socio_id": socio.json()["id"],
            "libro_id": records["libro"]["id"],
            "fecha_limite": "2030-01-01T00:00:00Z",
        },
    )
    assert prestamo.status_code == 201, prestamo.text
    assert client.get(f"/api/v1/libros/{records['libro']['id']}").json()["disponible"] == 0

    agotado = client.post(
        "/api/v1/prestamos",
        json={
            "socio_id": socio.json()["id"],
            "libro_id": records["libro"]["id"],
            "fecha_limite": "2030-01-01T00:00:00Z",
        },
    )
    assert agotado.status_code == 422

    devolucion = {"fecha_devolucion": "2030-01-03T00:00:00Z"}
    actualizado = client.patch(
        f"/api/v1/prestamos/{prestamo.json()['id']}",
        json=devolucion,
    )
    assert actualizado.status_code == 200
    assert actualizado.json()["multa"] == 2000
    client.patch(f"/api/v1/prestamos/{prestamo.json()['id']}", json=devolucion)
    assert client.get(f"/api/v1/libros/{records['libro']['id']}").json()["disponible"] == 1


def test_only_admin_can_write_and_cover_upload_persists(api_client, monkeypatch):
    client, role, test_session = api_client
    records = crear_libro(client)
    role["value"] = "user"
    assert client.get("/api/v1/libros").status_code == 200
    assert client.post("/api/v1/autores", json={"nombre": "Otro autor"}).status_code == 403

    role["value"] = "admin"

    def subir_portada(libro_id, archivo, nombre_original):
        return PortadaRespuesta(
            libro_id=libro_id,
            portada_url="https://res.cloudinary.com/demo/image/upload/cover.jpg",
            portada_public_id=f"biblioteca/portadas/libro_{libro_id}",
            formato="jpg",
            ancho=500,
            alto=700,
            bytes=321,
            nombre_original=nombre_original,
            miniatura_url="https://res.cloudinary.com/demo/image/upload/thumbnail.jpg",
        )

    monkeypatch.setattr(portadas, "subir_portada_cloudinary", subir_portada)
    response = client.post(
        f"/api/v1/libros/{records['libro']['id']}/portada",
        files={"archivo": ("cover.png", b"image-bytes", "image/png")},
    )
    assert response.status_code == 201, response.text

    with test_session() as db:
        libro = db.get(Libro, records["libro"]["id"])
        assert libro is not None
        assert libro.portada_url == "https://res.cloudinary.com/demo/image/upload/cover.jpg"
        assert libro.portada_public_id == f"biblioteca/portadas/libro_{libro.id}"


def test_book_creation_accepts_binary_cover(api_client):
    client, _, _ = api_client
    author = client.post("/api/v1/autores", json={"nombre": "Isabel Allende"})
    category = client.post("/api/v1/categorias", json={"nombre": "Ficción"})
    response = client.post(
        "/api/v1/libros",
        data={
            "titulo": "La casa de los espíritus",
            "isbn": "9789876543210",
            "autor_id": str(author.json()["id"]),
            "categoria_ids": [category.json()["id"]],
        },
        files={"archivo_portada": ("portada.png", b"image-bytes", "image/png")},
    )
    assert response.status_code == 201, response.text
    assert response.json()["portada_url"] == (
        "https://res.cloudinary.com/demo/image/upload/cover.jpg"
    )

    invalido = client.post(
        "/api/v1/libros",
        data={
            "titulo": "Libro con URL inválida",
            "isbn": "9789876543211",
            "autor_id": str(author.json()["id"]),
        },
        files={"archivo_portada": ("portada.txt", b"not-an-image", "text/plain")},
    )
    assert invalido.status_code == 415
