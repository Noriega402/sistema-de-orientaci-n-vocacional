from fastapi import APIRouter
from sqlalchemy import text

from app.db import engine

router = APIRouter(tags=["Historial"])


@router.get("/historial/{id_usuario}")
def historial(id_usuario: int):

    with engine.begin() as conn:

        historial = conn.execute(text("""
            SELECT *
            FROM resultado_test
            WHERE id_usuario = :id_usuario
            ORDER BY fecha DESC
        """), {
            "id_usuario": id_usuario
        }).fetchall()

        return [
            dict(x._mapping)
            for x in historial
        ]