from fastapi import APIRouter
from sqlalchemy import text

from app.db import engine


router = APIRouter(
    tags=["Preguntas"]
)


@router.get("/preguntas")
def obtener_preguntas():

    with engine.begin() as conn:

        preguntas = conn.execute(
            text("""
                SELECT
                    id_pregunta,
                    orden,
                    pregunta
                FROM preguntas
                ORDER BY orden ASC
            """)
        )


        respuestas = conn.execute(
            text("""
                SELECT
                    id_respuesta,
                    texto,
                    valor
                FROM respuestas
                ORDER BY valor ASC
            """)
        )


        preguntas_json = [
            dict(x._mapping)
            for x in preguntas
        ]


        respuestas_json = [
            dict(x._mapping)
            for x in respuestas
        ]


        return {

            "preguntas": preguntas_json,

            "respuestas": respuestas_json

        }
