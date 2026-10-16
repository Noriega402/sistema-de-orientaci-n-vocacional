import joblib

from sqlalchemy import text
from app.db import SessionLocal

modelo = joblib.load("model/modelo.pkl")

def resolver_test_service(data):

    db = SessionLocal()

    # CREAR RESULTADO
    resultado = db.execute(text("""
        INSERT INTO resultado_test (id_usuario)
        VALUES (:id_usuario)
        RETURNING id_resultado
    """), {
        "id_usuario": data.id_usuario
    })

    id_resultado = resultado.fetchone()[0]

    # GUARDAR RESPUESTAS
    for i, respuesta in enumerate(data.respuestas):

        id_pregunta = i + 1

        db.execute(text("""
            INSERT INTO respuesta_usuario
            (id_resultado, id_pregunta, id_respuesta)
            VALUES (:id_resultado, :id_pregunta, :id_respuesta)
        """), {
            "id_resultado": id_resultado,
            "id_pregunta": id_pregunta,
            "id_respuesta": respuesta
        })

    # IA
    probabilidades = modelo.predict_proba([data.respuestas])[0]

    top3 = sorted(
        enumerate(probabilidades),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    recomendaciones = []

    # TOP 3
    for posicion, (categoria_index, score) in enumerate(top3, start=1):

        categoria_id = categoria_index + 1

        maestria_query = db.execute(text("""
            SELECT id_maestria, nombre
            FROM maestrias
            WHERE categoria_id = :categoria_id
            LIMIT 1
        """), {
            "categoria_id": categoria_id
        })

        maestria = maestria_query.fetchone()

        if maestria:

            id_maestria = maestria[0]
            nombre_maestria = maestria[1]

            db.execute(text("""
                INSERT INTO recomendacion
                (id_resultado, id_maestria, posicion, puntaje)
                VALUES (:id_resultado, :id_maestria, :posicion, :puntaje)
            """), {
                "id_resultado": id_resultado,
                "id_maestria": id_maestria,
                "posicion": posicion,
                "puntaje": float(score)
            })

            recomendaciones.append({
                "posicion": posicion,
                "maestria": nombre_maestria,
                "puntaje": round(float(score) * 100, 2)
            })

    db.commit()
    db.close()

    return {
        "ok": True,
        "top3": recomendaciones
    }