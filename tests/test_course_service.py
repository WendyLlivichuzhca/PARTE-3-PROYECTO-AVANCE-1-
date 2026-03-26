import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database.connection as db_connection
from database.schema import initialize_database
from services.course_service import CourseService


class CourseServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db_path = db_connection.DB_PATH
        db_connection.DB_PATH = Path(self.temp_dir.name) / "test_sistema_cursos.db"
        initialize_database()
        self.service = CourseService()

    def tearDown(self):
        db_connection.DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def test_create_student_rejects_invalid_email(self):
        with self.assertRaises(ValueError):
            self.service.create_student("Ana", 21, "correo-invalido")

    def test_create_enrollment_requires_available_course(self):
        self.service.create_instructor("Luis Perez", "Python")
        self.service.create_student("Ana Torres", 20, "ana@email.com")
        self.service.create_course(
            "POO II",
            "Programacion",
            "Basico",
            1,
            35.0,
            "Curso introductorio",
        )

        with db_connection.get_connection() as connection:
            connection.execute(
                "UPDATE courses SET status = 'Cerrado' WHERE id = 1"
            )

        with self.assertRaises(ValueError):
            self.service.create_enrollment(1, 1, "Pagado")

    def test_generate_certificate_updates_enrollment(self):
        self.service.create_instructor("Luis Perez", "Python")
        self.service.create_student("Ana Torres", 20, "ana@email.com")
        self.service.create_course(
            "POO II",
            "Programacion",
            "Basico",
            1,
            35.0,
            "Curso introductorio",
        )
        self.service.create_enrollment(1, 1, "Pagado")
        self.service.update_progress(1, 100)

        with patch(
            "services.course_service.generate_certificate",
            return_value=str(Path(self.temp_dir.name) / "certificado.pdf"),
        ):
            pdf_path = self.service.generate_certificate_for_enrollment(1)

        self.assertTrue(pdf_path.endswith("certificado.pdf"))

        with db_connection.get_connection() as connection:
            row = connection.execute(
                "SELECT completed, certificate_path FROM enrollments WHERE id = 1"
            ).fetchone()

        self.assertEqual(row["completed"], 1)
        self.assertTrue(row["certificate_path"].endswith("certificado.pdf"))


if __name__ == "__main__":
    unittest.main()
