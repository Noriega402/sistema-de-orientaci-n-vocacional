from pydantic import BaseModel
from typing import List


class RespuestaItem(BaseModel):
    id_pregunta: int
    id_respuesta: int


class TestRequest(BaseModel):
    id_usuario: int
    respuestas: List[RespuestaItem]