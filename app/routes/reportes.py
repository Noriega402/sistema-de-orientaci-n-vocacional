import json
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import text
from app.db import engine
from app.services.pdf_service import generar_pdf_resultados

router = APIRouter(tags=['Reportes'])

@router.get('/resultados/{id_resultado}/pdf')
def descargar_pdf(id_resultado: int, id_usuario: int = Query(..., gt=0)):
    with engine.connect() as conn:
        registro = conn.execute(text('''
            SELECT r.id_resultado, r.fecha, r.resultados_completos, u.nombre
            FROM resultado_test r JOIN usuarios u ON u.id_usuario = r.id_usuario
            WHERE r.id_resultado = :id_resultado AND r.id_usuario = :id_usuario
        '''), {'id_resultado': id_resultado, 'id_usuario': id_usuario}).mappings().first()
    if registro is None:
        raise HTTPException(status_code=404, detail='No se encontró esta evaluación para el usuario indicado.')
    carreras = registro['resultados_completos']
    if isinstance(carreras, str): carreras = json.loads(carreras)
    if not carreras:
        raise HTTPException(status_code=409, detail='Esta evaluación anterior solo guardó el Top 3. Realiza un nuevo test para descargar todas las carreras.')
    pdf = generar_pdf_resultados(registro['nombre'], registro['fecha'], id_resultado, carreras)
    return Response(content=pdf, media_type='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="Vocare-resultados-{id_resultado}.pdf"',
        'Cache-Control': 'no-store'
    })
