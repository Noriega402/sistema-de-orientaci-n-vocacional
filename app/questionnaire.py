"""Contrato del cuestionario: orden de características compartido con entrenamiento."""
import json
from pathlib import Path
PREGUNTAS = json.loads(Path(__file__).with_name("questionnaire.json").read_text(encoding="utf-8"))
TOTAL_PREGUNTAS = len(PREGUNTAS)
