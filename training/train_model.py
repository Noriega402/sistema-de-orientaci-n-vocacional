import pandas as pd
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

RUTA_SCRIPT = Path(__file__).resolve().parent
RUTA_PROYECTO = RUTA_SCRIPT.parent

RUTA_DATASET = RUTA_SCRIPT / "dataset.csv"
RUTA_MODELO = RUTA_PROYECTO / "model" / "modelo.pkl"

print()
print("=" * 60)
print("ENTRENAMIENTO DEL MODELO VOCARE")
print("=" * 60)

print("\nCargando dataset...")

data = pd.read_csv(
    RUTA_DATASET
)

print(
    f"Registros cargados: {len(data)}"
)

print(
    f"Columnas encontradas: {len(data.columns)}"
)

X = data.drop(
    columns=["carrera"]
)

y = data["carrera"]


print()
print("=" * 60)
print("DATOS PARA EL MODELO")
print("=" * 60)

print(
    f"\nCaracterísticas de entrada: {X.shape[1]}"
)

print(
    f"Carreras disponibles: {y.nunique()}"
)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print()
print("=" * 60)
print("DIVISIÓN DEL DATASET")
print("=" * 60)

print(
    f"\nRegistros de entrenamiento: {len(X_train)}"
)

print(
    f"Registros de prueba: {len(X_test)}"
)

print()
print("=" * 60)
print("ENTRENANDO RANDOM FOREST")
print("=" * 60)

modelo = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

modelo.fit(
    X_train,
    y_train
)

print("\nEntrenamiento finalizado.")
predicciones = modelo.predict(
    X_test
)

accuracy = accuracy_score(
    y_test,
    predicciones
)

print()
print("=" * 60)
print("RESULTADOS DEL MODELO")
print("=" * 60)

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)

print()
print("=" * 60)
print("REPORTE DE CLASIFICACIÓN")
print("=" * 60)

print(
    classification_report(
        y_test,
        predicciones
    )
)

print()
print("=" * 60)
print("MATRIZ DE CONFUSIÓN")
print("=" * 60)

print(
    confusion_matrix(
        y_test,
        predicciones
    )
)

print()
print("=" * 60)
print("CARRERAS RECONOCIDAS POR EL MODELO")
print("=" * 60)

for numero, carrera in enumerate(
    modelo.classes_,
    start=1
):
    print(
        f"{numero}. {carrera}"
    )

RUTA_MODELO.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    modelo,
    RUTA_MODELO,
    compress=3
)


print()
print("=" * 60)
print("MODELO GUARDADO CORRECTAMENTE")
print("=" * 60)

print(
    f"\nArchivo generado en:\n{RUTA_MODELO}"
)

print()
print("El modelo espera:")
print(
    f"{modelo.n_features_in_} respuestas"
)

print()
print("=" * 60)
print("ENTRENAMIENTO FINALIZADO")
print("=" * 60)