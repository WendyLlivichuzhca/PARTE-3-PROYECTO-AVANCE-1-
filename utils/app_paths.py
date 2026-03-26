import os
import sys
from pathlib import Path


APP_NAME = "EduCampus"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_app_base_dir():
    """Devuelve una ruta escribible para la app instalada."""
    if getattr(sys, "frozen", False):
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            base_dir = Path(local_appdata)
        else:
            base_dir = Path.home() / "AppData" / "Local"
        app_dir = base_dir / APP_NAME
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir
    return PROJECT_ROOT


def get_database_path():
    return get_app_base_dir() / "sistema_cursos.db"


def get_certificates_dir():
    path = get_app_base_dir() / "certificados"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_downloads_dir():
    path = get_app_base_dir() / "materiales_descargados"
    path.mkdir(parents=True, exist_ok=True)
    return path
