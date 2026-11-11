from pathlib import Path
from django.conf import settings
from django.test import TestCase

BASE_DIR = Path(settings.BASE_DIR)

class DocumentosDisenioTest(TestCase):
    def test_docs_diagrama_er_existe(self):
        self.assertTrue((BASE_DIR / 'docs' / 'diagramas' / 'diagrama_er.md').exists())

    def test_diagrama_er_contiene_mermaid(self):
        path = BASE_DIR / 'docs' / 'diagramas' / 'diagrama_er.md'
        if path.exists():
            self.assertIn('mermaid', path.read_text(encoding='utf-8').lower())

    def test_diagrama_er_contiene_entidades_clave(self):
        path = BASE_DIR / 'docs' / 'diagramas' / 'diagrama_er.md'
        if path.exists():
            content = path.read_text(encoding='utf-8').upper()
            for entidad in ['CLIENTE', 'PRODUCTO', 'VENTA', 'PROVEEDOR', 'CATEGORIA', 'DETALLE_VENTA']:
                self.assertIn(entidad, content)

    def test_entidades_atributos_existe(self):
        self.assertTrue((BASE_DIR / 'docs' / 'entidades_atributos.md').exists())

    def test_decisiones_diseno_existe(self):
        self.assertTrue((BASE_DIR / 'docs' / 'decisiones_diseno.md').exists())

    def test_decisiones_diseno_tiene_contenido(self):
        path = BASE_DIR / 'docs' / 'decisiones_diseno.md'
        if path.exists():
            decisiones = [l for l in path.read_text(encoding='utf-8').splitlines() if l.startswith('### D-')]
            self.assertGreaterEqual(len(decisiones), 5)

    def test_sprint1_planning_existe(self):
        self.assertTrue((BASE_DIR / 'sprint1_planning.md').exists())

    def test_sprint1_planning_tiene_sprint_goal(self):
        path = BASE_DIR / 'sprint1_planning.md'
        if path.exists():
            self.assertIn('Sprint Goal', path.read_text(encoding='utf-8'))