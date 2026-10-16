import json
from app.questionnaire import TOTAL_PREGUNTAS
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.db import engine
from app.schemas.test_schema import TestRequest
from app.services.ia_service import obtener_recomendaciones


router = APIRouter()

@router.post("/guardar-test")
def guardar_test(data: TestRequest):

    if len(data.respuestas) != TOTAL_PREGUNTAS:
        raise HTTPException(
            status_code=400,
            detail=(
                "El test debe contener exactamente "
                f"{TOTAL_PREGUNTAS} respuestas."
            )
        )


    try:

        with engine.begin() as conn:

            usuario = conn.execute(
                text("""
                    SELECT id_usuario
                    FROM usuarios
                    WHERE id_usuario = :id_usuario
                """),
                {
                    "id_usuario": data.id_usuario
                }
            ).fetchone()


            if usuario is None:
                raise HTTPException(
                    status_code=404,
                    detail="El usuario no existe."
                )

            preguntas_bd = conn.execute(text("SELECT id_pregunta, orden FROM preguntas ORDER BY orden")).fetchall()
            if [q.orden for q in preguntas_bd] != list(range(1, TOTAL_PREGUNTAS + 1)):
                raise HTTPException(503, "Debe aplicar la migración del cuestionario de 60 preguntas.")
            por_id = {r.id_pregunta: r for r in data.respuestas}
            if len(por_id) != TOTAL_PREGUNTAS or set(por_id) != {q.id_pregunta for q in preguntas_bd}:
                raise HTTPException(400, "Las respuestas deben incluir cada pregunta vigente exactamente una vez.")
            respuestas_ordenadas = [por_id[q.id_pregunta] for q in preguntas_bd]

            respuestas_modelo = []


            for r in respuestas_ordenadas:

                pregunta = conn.execute(
                    text("""
                        SELECT
                            id_pregunta,
                            orden
                        FROM preguntas
                        WHERE id_pregunta = :id_pregunta
                    """),
                    {
                        "id_pregunta": r.id_pregunta
                    }
                ).fetchone()


                if pregunta is None:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"La pregunta "
                            f"{r.id_pregunta} no existe."
                        )
                    )

                respuesta = conn.execute(
                    text("""
                        SELECT
                            id_respuesta,
                            valor
                        FROM respuestas
                        WHERE id_respuesta = :id_respuesta
                    """),
                    {
                        "id_respuesta": r.id_respuesta
                    }
                ).fetchone()


                if respuesta is None:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"La respuesta "
                            f"{r.id_respuesta} no existe."
                        )
                    )

                respuestas_modelo.append(
                    respuesta.valor
                )

            todas = obtener_recomendaciones(
                respuestas_modelo, todas=True
            )

            resultado = conn.execute(
                text("""
                    INSERT INTO resultado_test
                    (
                        id_usuario
                    )
                    VALUES
                    (
                        :id_usuario
                    )
                    RETURNING id_resultado
                """),
                {
                    "id_usuario": data.id_usuario
                }
            )


            id_resultado = resultado.fetchone()[0]

            for r in respuestas_ordenadas:

                conn.execute(
                    text("""
                        INSERT INTO respuesta_usuario
                        (
                            id_resultado,
                            id_pregunta,
                            id_respuesta
                        )
                        VALUES
                        (
                            :id_resultado,
                            :id_pregunta,
                            :id_respuesta
                        )
                    """),
                    {
                        "id_resultado": id_resultado,
                        "id_pregunta": r.id_pregunta,
                        "id_respuesta": r.id_respuesta
                    }
                )

            recomendaciones_finales = []


            for item in todas:

                carrera = conn.execute(
                    text("""
                        SELECT
                            id_carrera,
                            nombre,
                            descripcion,
                            area,
                            duracion,
                            modalidad
                        FROM carreras
                        WHERE nombre = :nombre
                    """),
                    {
                        "nombre": item["carrera"]
                    }
                ).fetchone()


                if carrera is None:
                    raise HTTPException(
                        status_code=500,
                        detail=(
                            "La carrera recomendada por "
                            f"el modelo no existe en la BD: "
                            f"{item['carrera']}"
                        )
                    )

                if item["posicion"] <= 3:
                    conn.execute(
                        text("""
                            INSERT INTO recomendacion
                            (
                                id_resultado,
                                id_carrera,
                                posicion,
                                probabilidad
                            )
                            VALUES
                            (
                                :id_resultado,
                                :id_carrera,
                                :posicion,
                                :probabilidad
                            )
                        """),
                        {
                            "id_resultado": id_resultado,
                            "id_carrera": carrera.id_carrera,
                            "posicion": item["posicion"],
                            "probabilidad": item["probabilidad"]
                        }
                    )
    
                recomendaciones_finales.append({

                    "posicion": item["posicion"],

                    "id_carrera": carrera.id_carrera,

                    "nombre": carrera.nombre,

                    "descripcion": carrera.descripcion,

                    "area": carrera.area,

                    "duracion": carrera.duracion,

                    "modalidad": carrera.modalidad,

                    "probabilidad": item["probabilidad"]

                })

            conn.execute(text("""
                UPDATE resultado_test
                SET resultados_completos = CAST(:resultados AS JSONB)
                WHERE id_resultado = :id_resultado
            """), {"resultados": json.dumps(recomendaciones_finales, ensure_ascii=False),
                    "id_resultado": id_resultado})

            return {

                "message": "Test guardado correctamente",

                "id_resultado": id_resultado,

                "top3": recomendaciones_finales[:3],
                "carreras": recomendaciones_finales

            }


    except HTTPException:
        raise


    except Exception as error:

        print(
            "Error guardando test:",
            error
        )

        raise HTTPException(
            status_code=500,
            detail="Error interno al procesar el test."
        )