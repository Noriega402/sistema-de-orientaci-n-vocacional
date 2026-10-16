import joblib

modelo = joblib.load("model/modelo.pkl")

def predecir(vector):
    return modelo.predict([vector])[0]

def top3(vector):
    probs = modelo.predict_proba([vector])[0]
    clases = modelo.classes_

    resultados = sorted(
        zip(clases, probs),
        key=lambda x: x[1],
        reverse=True
    )

    return resultados[:3]