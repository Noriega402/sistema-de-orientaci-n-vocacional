import pandas as pd
from app.db import engine

def cargar_pesos():
    query = """
    SELECT pregunta_id, categoria_id, peso
    FROM pesos_categoria
    """
    return pd.read_sql(query, engine)