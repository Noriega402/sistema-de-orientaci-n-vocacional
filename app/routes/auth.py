from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.db import engine

from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest
)

from app.models.security import (
    hash_password,
    verify_password
)


router = APIRouter(
    tags=["Autenticación"]
)

@router.post("/register")
def register(data: RegisterRequest):

    correo = data.correo.lower().strip()
    nombre = data.nombre.strip()

    try:

        with engine.begin() as conn:

            usuario_existente = conn.execute(
                text("""
                    SELECT id_usuario
                    FROM usuarios
                    WHERE LOWER(correo) = :correo
                """),
                {
                    "correo": correo
                }
            ).fetchone()


            if usuario_existente:

                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Ya existe un usuario "
                        "registrado con este correo."
                    )
                )

            password_hash = hash_password(
                data.password
            )

            resultado = conn.execute(
                text("""
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
                        :password_hash
                    )
                    RETURNING
                        id_usuario,
                        nombre,
                        correo,
                        fecha_registro
                """),
                {
                    "nombre": nombre,
                    "correo": correo,
                    "password_hash": password_hash
                }
            )


            usuario = resultado.fetchone()

            return {

                "message": (
                    "Usuario registrado correctamente."
                ),

                "usuario": {
                    "id_usuario": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "correo": usuario.correo
                }

            }


    except HTTPException:
        raise


    except Exception as error:

        print("ERROR EN REGISTRO:", error)

        raise HTTPException(
            status_code=500,
            detail=(
                "Error interno al registrar el usuario."
            )
        )

@router.post("/login")
def login(data: LoginRequest):

    correo = data.correo.lower().strip()

    try:

        with engine.connect() as conn:

            usuario = conn.execute(
                text("""
                    SELECT
                        id_usuario,
                        nombre,
                        correo,
                        password_hash
                    FROM usuarios
                    WHERE LOWER(correo) = :correo
                """),
                {
                    "correo": correo
                }
            ).fetchone()

            if usuario is None:

                raise HTTPException(
                    status_code=401,
                    detail=(
                        "Correo o contraseña incorrectos."
                    )
                )

            password_valido = verify_password(
                data.password,
                usuario.password_hash
            )


            if not password_valido:

                raise HTTPException(
                    status_code=401,
                    detail=(
                        "Correo o contraseña incorrectos."
                    )
                )

            return {

                "message": (
                    "Inicio de sesión correcto."
                ),

                "usuario": {
                    "id_usuario": usuario.id_usuario,
                    "nombre": usuario.nombre,
                    "correo": usuario.correo
                }

            }


    except HTTPException:
        raise


    except Exception as error:

        print(
            "ERROR EN LOGIN:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Error interno al iniciar sesión."
            )
        )