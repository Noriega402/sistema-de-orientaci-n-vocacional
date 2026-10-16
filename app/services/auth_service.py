from sqlalchemy import text
from app.db import engine


def register_user(nombre, correo, password):

    with engine.begin() as conn:

        existe = conn.execute(text("""

            SELECT *
            FROM usuarios
            WHERE correo = :correo

        """), {

            "correo": correo

        }).fetchone()

        if existe:

            raise Exception(
                "Correo ya registrado"
            )

        conn.execute(text("""

            INSERT INTO usuarios
            (
                nombre,
                correo,
                password_hash
            )
            VALUES
            (
                :nombre,
                :correo,
                :password
            )

        """), {

            "nombre": nombre,
            "correo": correo,
            "password": password
        })


def login_user(correo, password):

    with engine.begin() as conn:

        usuario = conn.execute(text("""

            SELECT
                id_usuario,
                nombre,
                correo
            FROM usuarios
            WHERE correo = :correo
            AND password_hash = :password

        """), {

            "correo": correo,
            "password": password

        }).fetchone()

        if not usuario:
            return None

        return dict(usuario._mapping)