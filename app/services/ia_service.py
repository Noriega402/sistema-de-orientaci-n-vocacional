import joblib
import numpy as np
import pandas as pd
from app.questionnaire import TOTAL_PREGUNTAS
from pathlib import Path

RUTA_ACTUAL = Path(__file__).resolve().parent

RUTA_PROYECTO = (
    RUTA_ACTUAL
    .parent
    .parent
)

RUTA_MODELO = (
    RUTA_PROYECTO
    / "model"
    / "modelo.pkl"
)

modelo = joblib.load(
    RUTA_MODELO
)

if modelo.n_features_in_ != TOTAL_PREGUNTAS:
    raise RuntimeError("Modelo incompatible: vuelva a ejecutar training/train_model.py")

def obtener_recomendaciones(respuestas, todas=False):

    if len(respuestas) != TOTAL_PREGUNTAS:

        raise ValueError(
            "El modelo necesita exactamente "
            f"{TOTAL_PREGUNTAS} respuestas. Se recibieron {len(respuestas)}."
        )

    for respuesta in respuestas:

        if respuesta < 1 or respuesta > 5:

            raise ValueError(
                "Todas las respuestas deben "
                "tener valores entre 1 y 5."
            )

    X = pd.DataFrame([respuestas], columns=[f"pregunta_{i}" for i in range(1, TOTAL_PREGUNTAS + 1)])

    probabilidades = modelo.predict_proba(
        X
    )[0]

    carreras = modelo.classes_

    indices_top = np.argsort(
        probabilidades
    )[::-1]
    if not todas:
        indices_top = indices_top[:3]

    recomendaciones = []

    for posicion, indice in enumerate(
        indices_top,
        start=1
    ):

        recomendaciones.append({

            "posicion": posicion,

            "carrera": str(carreras[indice]),

            "probabilidad": round(
                float(
                    probabilidades[indice]
                ) * 100,
                2
            )
        })

    return recomendaciones