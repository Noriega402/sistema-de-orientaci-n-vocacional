def aplicar_reglas(vector, recomendaciones):
    
    if vector[0] < 20:
        recomendaciones = [r for r in recomendaciones if r != "Data Science"]

    return recomendaciones