"""Suite de pruebas W03 — Archivos de despliegue y configuración."""
import os
from pathlib import Path

from django.conf import settings
from django.test import TestCase

BASE_DIR = Path(settings.BASE_DIR)


class ArchivosDespliegueTest(TestCase):
    def test_procfile_existe(self):
        self.assertTrue((BASE_DIR / 'Procfile').exists(), "Procfile no encontrado")

    def test_procfile_contiene_gunicorn(self):
        procfile = BASE_DIR / 'Procfile'
        if procfile.exists():
            content = procfile.read_text(encoding='utf-8')
            self.assertIn('gunicorn', content, "Procfile debe usar gunicorn")

    def test_render_yaml_existe(self):
        self.assertTrue((BASE_DIR / 'render.yaml').exists(), "render.yaml no encontrado")

    def test_ficha_schmelkes_e1_existe(self):
        self.assertTrue((BASE_DIR / 'fichas' / 'espiral_01_infra.md').exists(), "Ficha E1 no encontrada")


class RequirementsProduccionTest(TestCase):
    def _leer_requirements(self):
        req_path = BASE_DIR / 'requirements.txt'
        if not req_path.exists():
            self.fail("requirements.txt no encontrado")
        return req_path.read_text(encoding='utf-8').lower()

    def test_gunicorn_en_requirements(self):
        self.assertIn('gunicorn', self._leer_requirements())

    def test_psycopg2_en_requirements(self):
        self.assertIn('psycopg2', self._leer_requirements())

    def test_dj_database_url_en_requirements(self):
        self.assertIn('dj-database-url', self._leer_requirements())


class SettingsProdTest(TestCase):
    def _leer_settings_prod(self):
        path = BASE_DIR / 'core' / 'settings_prod.py'
        if not path.exists():
            self.fail("core/settings_prod.py no encontrado")
        return path.read_text(encoding='utf-8')

    def test_settings_prod_tiene_debug_false(self):
        content = self._leer_settings_prod()
        self.assertIn('DEBUG = False', content)

    def test_settings_prod_importa_dj_database_url(self):
        content = self._leer_settings_prod()
        self.assertIn('dj_database_url', content)