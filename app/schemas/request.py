from pydantic import BaseModel

class RespuestasRequest(BaseModel):
    respuestas: dict