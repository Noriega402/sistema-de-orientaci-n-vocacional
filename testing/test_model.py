"""Ejecutar desde la raíz: python -m unittest discover -s testing -v"""
import unittest
import importlib.util
from pathlib import Path
from datetime import datetime
from app.questionnaire import TOTAL_PREGUNTAS, PREGUNTAS
from app.services.ia_service import obtener_recomendaciones, modelo
from app.services.pdf_service import generar_pdf_resultados

class ModeloTest(unittest.TestCase):
    def test_contrato(self):
        self.assertEqual(TOTAL_PREGUNTAS, 60)
        self.assertEqual(modelo.n_features_in_, 60)
        self.assertEqual(len(modelo.classes_), 15)
        self.assertEqual([q['orden'] for q in PREGUNTAS], list(range(1,61)))

    def test_perfiles_y_pdf(self):
        spec = importlib.util.spec_from_file_location('generador', Path('training/generate_fake_data.py'))
        g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
        for carrera, perfil in g.PERFILES.items():
            with self.subTest(carrera=carrera):
                respuestas = [5 if i in perfil['principales'] else 4 if i in perfil['secundarias'] else 2 for i in range(1,61)]
                resultados = obtener_recomendaciones(respuestas, todas=True)
                self.assertEqual(resultados[0]['carrera'], carrera)
                self.assertEqual(len(resultados), 15)
                self.assertAlmostEqual(sum(r['probabilidad'] for r in resultados),100,delta=.1)
                self.assertEqual(len(obtener_recomendaciones(respuestas)),3)
        pdf = generar_pdf_resultados('Prueba', datetime(2026,10,16),1,[dict(nombre=r['carrera'],**r) for r in resultados])
        self.assertTrue(pdf.startswith(b'%PDF'))

    def test_invalidos(self):
        for r in ([3]*35,[3]*59,[3]*61,[0]*60,[6]*60):
            with self.subTest(longitud=len(r)), self.assertRaises(ValueError):
                obtener_recomendaciones(r)

if __name__ == '__main__': unittest.main()
