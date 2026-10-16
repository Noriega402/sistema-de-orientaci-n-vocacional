def calcular_vector_usuario(respuestas_usuario, df_pesos):
    resultado = {}

    for _, row in df_pesos.iterrows():
        pregunta = row["pregunta_id"]
        categoria = row["categoria_id"]
        peso = row["peso"]

        valor = respuestas_usuario.get(str(pregunta), 0)

        resultado[categoria] = resultado.get(categoria, 0) + (valor * peso)

    return resultado


def vector_a_lista(vector_dict):
    return [vector_dict[k] for k in sorted(vector_dict.keys())]