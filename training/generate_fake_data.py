import random
import pandas as pd
from pathlib import Path

TOTAL_REGISTROS = 15000
TOTAL_PREGUNTAS = 60
SEMILLA = 42

random.seed(SEMILLA)

PERFILES = {

    "Ingeniería en Sistemas": {

        "principales": [
            1,   # Funcionamiento de computadoras y sistemas
            2,   # Lógica y razonamiento
            3,   # Programación
            4,   # Diseño de sistemas
            11,  # Problemas tecnológicos
            12,  # Comunicación entre dispositivos
            17   # Buscar y corregir errores
        ],

        "secundarias": [
            5,   # Análisis de información
            8,   # Investigación de problemas
            9,   # Seguridad informática
            13,  # Redes y servidores
            15,  # Desarrollo de sistemas
            16   # Crear y mejorar soluciones
        ],

        "bajas": [
            22,
            24,
            30,
            31,
            32
        ]
    },

    "Ciencia de Datos": {

        "principales": [
            2,   # Lógica
            5,   # Análisis de información
            6,   # Matemática y estadística
            7,   # Predicciones mediante datos
            8,   # Investigación
            29   # Análisis para detectar irregularidades
        ],

        "secundarias": [
            1,   # Tecnología
            3,   # Programación
            11,  # Atención a problemas tecnológicos
            17,  # Resolución de errores
            27,  # Información financiera
            28,  # Atención al detalle
            34   # Mejora de procesos
        ],

        "bajas": [
            22,
            24,
            25,
            30,
            31
        ]
    },

    "Ingeniería en Ciberseguridad": {

        "principales": [
            1,   # Sistemas tecnológicos
            2,   # Lógica
            8,   # Investigación de problemas
            9,   # Protección de sistemas
            10,  # Amenazas y vulnerabilidades
            11,  # Problemas tecnológicos
            17,  # Búsqueda de errores
            28   # Atención al detalle
        ],

        "secundarias": [
            3,   # Programación
            12,  # Redes
            13,  # Servidores
            14,  # Internet y comunicaciones
            29   # Detección de irregularidades
        ],

        "bajas": [
            22,
            23,
            24,
            25,
            31
        ]
    },

    "Ingeniería de Software": {

        "principales": [
            1,   # Sistemas tecnológicos
            2,   # Lógica
            3,   # Programación
            4,   # Diseño de aplicaciones
            15,  # Desarrollo de software
            16,  # Crear soluciones
            17   # Corrección de errores
        ],

        "secundarias": [
            5,   # Análisis de información
            8,   # Investigación
            11,  # Problemas tecnológicos
            28   # Atención al detalle
        ],

        "bajas": [
            24,
            26,
            27,
            30,
            31
        ]
    },

    "Ingeniería en Telecomunicaciones": {

        "principales": [
            1,   # Tecnología
            2,   # Lógica
            11,  # Problemas tecnológicos
            12,  # Comunicación de dispositivos
            13,  # Redes y servidores
            14,  # Internet, señales y comunicaciones
            17   # Resolución de problemas
        ],

        "secundarias": [
            3,   # Programación
            6,   # Matemáticas
            8,   # Investigación
            9,   # Seguridad
            16   # Mejora de soluciones
        ],

        "bajas": [
            22,
            24,
            25,
            30,
            31
        ]
    },

    "Administración de Empresas": {

        "principales": [
            18,  # Organización de personas y recursos
            19,  # Liderazgo
            20,  # Funcionamiento de empresas
            21,  # Administrar negocio
            27,  # Recursos financieros
            35   # Reducción de costos y recursos
        ],

        "secundarias": [
            7,   # Toma de decisiones
            16,  # Mejora continua
            23,  # Comportamiento del consumidor
            26,  # Presupuestos
            33,  # Comunicación
            34   # Mejora de procesos
        ],

        "bajas": [
            3,
            9,
            10,
            12,
            14
        ]
    },

    "Mercadotecnia": {

        "principales": [
            21,  # Negocios
            22,  # Comunicación creativa
            23,  # Comportamiento del consumidor
            24,  # Publicidad y redes sociales
            25,  # Creatividad
            32,  # Comportamiento humano
            33   # Comunicación
        ],

        "secundarias": [
            18,  # Organización
            19,  # Liderazgo
            20,  # Empresas
            30,  # Escuchar personas
            31   # Ayudar/comprender personas
        ],

        "bajas": [
            9,
            10,
            12,
            13,
            14
        ]
    },

    "Contaduría Pública y Auditoría": {

        "principales": [
            6,   # Matemáticas
            20,  # Empresas
            26,  # Cálculos y presupuestos
            27,  # Recursos financieros
            28,  # Revisión de números
            29,  # Detección de irregularidades
            35   # Reducción de costos
        ],

        "secundarias": [
            2,   # Lógica
            5,   # Análisis
            7,   # Toma de decisiones
            8,   # Investigación
            18,  # Organización
            34   # Mejora de procesos
        ],

        "bajas": [
            3,
            12,
            14,
            24,
            31
        ]
    },

    "Psicología": {

        "principales": [
            23,  # Motivaciones humanas
            30,  # Escuchar y comprender
            31,  # Ayudar a las personas
            32,  # Comportamiento humano
            33   # Empatía y comunicación
        ],

        "secundarias": [
            8,   # Investigación
            18,  # Organización
            19,  # Liderazgo
            22,  # Comunicación
            25   # Creatividad
        ],

        "bajas": [
            3,
            9,
            12,
            13,
            14
        ]
    },

    "Ingeniería Industrial": {

        "principales": [
            2,   # Lógica
            6,   # Matemáticas
            7,   # Toma de decisiones
            16,  # Mejora continua
            18,  # Organización de recursos
            34,  # Optimización de procesos
            35   # Reducción de tiempo y costos
        ],

        "secundarias": [
            5,   # Análisis de información
            8,   # Investigación
            19,  # Liderazgo
            20,  # Empresas
            26,  # Presupuestos
            27,  # Recursos financieros
            28   # Atención al detalle
        ],

        "bajas": [
            9,
            10,
            12,
            24,
            31
        ]
    }
}

# Preguntas 36–60: cinco dimensiones específicas por nueva carrera.
PERFILES['Ingeniería Química'] = {'principales': [36, 37, 38, 39, 40], 'secundarias': [6, 8, 34, 53], 'bajas': []}
PERFILES['Ingeniería Civil'] = {'principales': [41, 42, 43, 44, 45], 'secundarias': [2, 6, 18, 34], 'bajas': []}
PERFILES['Derecho'] = {'principales': [46, 47, 48, 49, 50], 'secundarias': [8, 28, 30, 33], 'bajas': []}
PERFILES['Biología'] = {'principales': [51, 52, 53, 54, 55], 'secundarias': [5, 8, 36, 56], 'bajas': []}
PERFILES['Medicina'] = {'principales': [56, 57, 58, 59, 60], 'secundarias': [8, 30, 31, 53], 'bajas': []}

# No se presupone desinterés por otras profesiones: valores neutrales con variación.
for perfil in PERFILES.values():
    perfil["bajas"] = []

def generar_respuesta(numero_pregunta, perfil):

    principales = perfil["principales"]
    secundarias = perfil["secundarias"]
    bajas = perfil["bajas"]

    if numero_pregunta in principales:

        return random.choices(
            population=[3, 4, 5],
            weights=[10, 40, 50],
            k=1
        )[0]

    if numero_pregunta in secundarias:

        return random.choices(
            population=[2, 3, 4, 5],
            weights=[5, 25, 45, 25],
            k=1
        )[0]

    if numero_pregunta in bajas:

        return random.choices(
            population=[1, 2, 3, 4],
            weights=[35, 40, 20, 5],
            k=1
        )[0]

    return random.choices(
        population=[1, 2, 3, 4, 5],
        weights=[10, 20, 40, 20, 10],
        k=1
    )[0]

def generar_dataset():

    registros = []

    carreras = list(PERFILES.keys())
    registros_por_carrera = TOTAL_REGISTROS // len(carreras)

    for carrera in carreras:

        perfil = PERFILES[carrera]

        for _ in range(registros_por_carrera):

            respuestas = []

            for numero_pregunta in range(
                1,
                TOTAL_PREGUNTAS + 1
            ):

                respuesta = generar_respuesta(
                    numero_pregunta,
                    perfil
                )

                respuestas.append(respuesta)

            respuestas.append(carrera)

            registros.append(respuestas)

    random.shuffle(registros)

    columnas = [
        f"pregunta_{i}"
        for i in range(
            1,
            TOTAL_PREGUNTAS + 1
        )
    ]

    columnas.append("carrera")

    df = pd.DataFrame(
        registros,
        columns=columnas
    )

    ruta_script = Path(__file__).resolve().parent

    ruta_dataset = (
        ruta_script
        / "dataset.csv"
    )

    df.to_csv(
        ruta_dataset,
        index=False,
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("DATASET VOCARE GENERADO CORRECTAMENTE")
    print("=" * 60)

    print(
        f"\nTotal de registros: {len(df)}"
    )

    print(
        f"Total de preguntas: {TOTAL_PREGUNTAS}"
    )

    print(
        f"Total de carreras: {len(carreras)}"
    )

    print(
        f"\nArchivo generado en:\n{ruta_dataset}"
    )

    print()
    print("=" * 60)
    print("DISTRIBUCIÓN DE CARRERAS")
    print("=" * 60)

    print(
        df["carrera"]
        .value_counts()
        .sort_index()
    )

    print()
    print("=" * 60)
    print("VALIDACIONES")
    print("=" * 60)


    # Validar valores mínimos y máximos
    columnas_preguntas = [
        f"pregunta_{i}"
        for i in range(
            1,
            TOTAL_PREGUNTAS + 1
        )
    ]

    valor_minimo = (
        df[columnas_preguntas]
        .min()
        .min()
    )

    valor_maximo = (
        df[columnas_preguntas]
        .max()
        .max()
    )

    print(
        f"Valor mínimo de respuesta: {valor_minimo}"
    )

    print(
        f"Valor máximo de respuesta: {valor_maximo}"
    )


    # Validar cantidad de columnas
    print(
        f"Cantidad de columnas: {len(df.columns)}"
    )

    print(
        "Esperado: 61 "
        "(60 preguntas + carrera)"
    )

    print()
    print("=" * 60)
    print("EJEMPLO DE REGISTRO")
    print("=" * 60)

    print(
        df.head(1).to_string(
            index=False
        )
    )

    print()
    print("=" * 60)
    print("FINALIZADO")
    print("=" * 60)

if __name__ == "__main__":

    generar_dataset()