from database.connection import get_connection
from utils.app_paths import get_certificates_dir
from utils.pdf_generator import generate_certificate


class CourseService:
    LEVELS = ("Basico", "Intermedio", "Avanzado")
    PAYMENT_STATES = ("Pendiente", "Pagado")

    def create_instructor(self, name, specialty):
        if not name.strip() or not specialty.strip():
            raise ValueError("Ingrese nombre y especialidad del instructor.")

        with get_connection() as connection:
            connection.execute(
                "INSERT INTO instructors(name, specialty) VALUES(?, ?)",
                (name.strip(), specialty.strip()),
            )

    def create_student(self, name, age, email):
        if not name.strip():
            raise ValueError("Ingrese el nombre del estudiante.")
        if age <= 0:
            raise ValueError("La edad debe ser mayor a cero.")
        if "@" not in email or "." not in email:
            raise ValueError("Ingrese un correo valido.")

        with get_connection() as connection:
            connection.execute(
                "INSERT INTO students(name, age, email) VALUES(?, ?, ?)",
                (name.strip(), age, email.strip().lower()),
            )

    def create_course(self, name, category, level, instructor_id, price, description):
        if not name.strip():
            raise ValueError("Ingrese el nombre del curso.")
        if not category.strip():
            raise ValueError("Ingrese la categoria del curso.")
        if level not in self.LEVELS:
            raise ValueError("Seleccione un nivel valido.")
        if instructor_id is None:
            raise ValueError("Seleccione un instructor.")
        if price < 0:
            raise ValueError("El precio no puede ser negativo.")

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO courses(name, category, level, instructor_id, price, description)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    name.strip(),
                    category.strip(),
                    level,
                    instructor_id,
                    float(price),
                    description.strip(),
                ),
            )

    def create_enrollment(self, student_id, course_id, payment_status):
        if student_id is None or course_id is None:
            raise ValueError("Seleccione estudiante y curso.")
        if payment_status not in self.PAYMENT_STATES:
            raise ValueError("Estado de pago invalido.")

        with get_connection() as connection:
            course = connection.execute(
                "SELECT status FROM courses WHERE id = ?", (course_id,)
            ).fetchone()
            if not course:
                raise ValueError("El curso no existe.")
            if course["status"] != "Disponible":
                raise ValueError("El curso no esta disponible.")

            connection.execute(
                """
                INSERT INTO enrollments(student_id, course_id, payment_status)
                VALUES(?, ?, ?)
                """,
                (student_id, course_id, payment_status),
            )

    def update_progress(self, enrollment_id, progress):
        if enrollment_id is None:
            raise ValueError("Seleccione una inscripcion.")
        if progress < 0 or progress > 100:
            raise ValueError("El progreso debe estar entre 0 y 100.")

        completed = 1 if progress == 100 else 0
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE enrollments
                SET progress = ?, completed = ?
                WHERE id = ?
                """,
                (progress, completed, enrollment_id),
            )

    def register_payment(self, enrollment_id):
        if enrollment_id is None:
            raise ValueError("Seleccione una inscripcion.")

        with get_connection() as connection:
            connection.execute(
                "UPDATE enrollments SET payment_status = 'Pagado' WHERE id = ?",
                (enrollment_id,),
            )

    def create_material(self, course_id, title, url, material_type):
        if course_id is None:
            raise ValueError("Seleccione un curso.")
        if not title.strip() or not url.strip():
            raise ValueError("Ingrese titulo y enlace del material.")

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO materials(course_id, title, url, material_type)
                VALUES(?, ?, ?, ?)
                """,
                (course_id, title.strip(), url.strip(), material_type.strip()),
            )

    def create_forum_message(
        self, course_id, sender_type, message, student_id=None, instructor_id=None
    ):
        if course_id is None:
            raise ValueError("Seleccione un curso.")
        if sender_type not in ("Estudiante", "Instructor"):
            raise ValueError("Tipo de remitente invalido.")
        if not message.strip():
            raise ValueError("Ingrese un mensaje.")

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO forum_messages(
                    course_id, student_id, instructor_id, sender_type, message
                ) VALUES(?, ?, ?, ?, ?)
                """,
                (course_id, student_id, instructor_id, sender_type, message.strip()),
            )

    def create_quiz_question(
        self, course_id, question, option_a, option_b, option_c, option_d, correct_option
    ):
        if course_id is None:
            raise ValueError("Seleccione un curso.")
        if correct_option not in ("A", "B", "C", "D"):
            raise ValueError("Seleccione una respuesta correcta valida.")
        values = [question, option_a, option_b, option_c, option_d]
        if not all(value.strip() for value in values):
            raise ValueError("Complete todos los campos del quiz.")

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO quiz_questions(
                    course_id, question, option_a, option_b, option_c, option_d, correct_option
                ) VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    course_id,
                    question.strip(),
                    option_a.strip(),
                    option_b.strip(),
                    option_c.strip(),
                    option_d.strip(),
                    correct_option,
                ),
            )

    def submit_quiz_attempt(self, enrollment_id, question_id, selected_option):
        if enrollment_id is None or question_id is None:
            raise ValueError("Seleccione inscripcion y pregunta.")
        if selected_option not in ("A", "B", "C", "D"):
            raise ValueError("Seleccione una opcion valida.")

        with get_connection() as connection:
            question = connection.execute(
                "SELECT correct_option FROM quiz_questions WHERE id = ?",
                (question_id,),
            ).fetchone()
            if not question:
                raise ValueError("La pregunta no existe.")

            score = 100 if selected_option == question["correct_option"] else 0
            status = "Aprobado" if score == 100 else "Reprobado"
            connection.execute(
                """
                INSERT INTO quiz_attempts(enrollment_id, question_id, selected_option, score, status)
                VALUES(?, ?, ?, ?, ?)
                """,
                (enrollment_id, question_id, selected_option, score, status),
            )
        return score, status

    def create_review(self, course_id, student_id, rating, comment):
        if course_id is None or student_id is None:
            raise ValueError("Seleccione curso y estudiante.")
        if rating < 1 or rating > 5:
            raise ValueError("La valoracion debe estar entre 1 y 5 estrellas.")
        if not comment.strip():
            raise ValueError("Ingrese un comentario.")

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO reviews(course_id, student_id, rating, comment)
                VALUES(?, ?, ?, ?)
                """,
                (course_id, student_id, rating, comment.strip()),
            )

    def generate_certificate_for_enrollment(self, enrollment_id):
        if enrollment_id is None:
            raise ValueError("Seleccione una inscripcion.")

        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT e.progress, s.name AS student_name, c.name AS course_name
                FROM enrollments e
                JOIN students s ON s.id = e.student_id
                JOIN courses c ON c.id = e.course_id
                WHERE e.id = ?
                """,
                (enrollment_id,),
            ).fetchone()
            if not row:
                raise ValueError("La inscripcion no existe.")
            if row["progress"] < 100:
                raise ValueError("Solo se genera certificado con 100% de progreso.")

            certificates_dir = get_certificates_dir()
            pdf_path = generate_certificate(
                row["student_name"], row["course_name"], certificates_dir
            )
            connection.execute(
                "UPDATE enrollments SET certificate_path = ?, completed = 1 WHERE id = ?",
                (pdf_path, enrollment_id),
            )
        return pdf_path

    def get_instructors(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT id, name, specialty FROM instructors ORDER BY name"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_students(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT id, name, age, email FROM students ORDER BY name"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_courses(self, level=None):
        query = """
            SELECT c.id, c.name, c.category, c.level, c.price, c.status,
                   i.name AS instructor_name
            FROM courses c
            JOIN instructors i ON i.id = c.instructor_id
        """
        params = []
        if level:
            query += " WHERE c.level = ?"
            params.append(level)
        query += " ORDER BY c.name"

        with get_connection() as connection:
            rows = connection.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_enrollments(self):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT e.id, s.name AS student_name, c.name AS course_name,
                       c.price, e.progress, e.payment_status, e.completed,
                       COALESCE(e.certificate_path, '') AS certificate_path,
                       e.course_id, e.student_id
                FROM enrollments e
                JOIN students s ON s.id = e.student_id
                JOIN courses c ON c.id = e.course_id
                ORDER BY e.purchased_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_materials(self):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT m.id, c.name AS course_name, m.title, m.url, m.material_type
                FROM materials m
                JOIN courses c ON c.id = m.course_id
                ORDER BY c.name, m.title
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_forum_messages(self):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT f.id, c.name AS course_name, f.sender_type, f.message, f.created_at
                FROM forum_messages f
                JOIN courses c ON c.id = f.course_id
                ORDER BY f.created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_quiz_questions(self):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT q.id, q.course_id, c.name AS course_name,
                       q.question, q.option_a, q.option_b, q.option_c, q.option_d,
                       q.correct_option
                FROM quiz_questions q
                JOIN courses c ON c.id = q.course_id
                ORDER BY c.name, q.id
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_reviews(self):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT r.id, c.name AS course_name, s.name AS student_name,
                       r.rating, r.comment, r.created_at
                FROM reviews r
                JOIN courses c ON c.id = r.course_id
                JOIN students s ON s.id = r.student_id
                ORDER BY r.created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_quiz_attempts(self):
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT qa.id,
                       s.name  AS student_name,
                       c.name  AS course_name,
                       qq.question,
                       qa.selected_option,
                       qq.correct_option,
                       qa.score,
                       qa.status,
                       qa.attempted_at
                FROM quiz_attempts qa
                JOIN enrollments e  ON e.id  = qa.enrollment_id
                JOIN students s     ON s.id  = e.student_id
                JOIN courses c      ON c.id  = e.course_id
                JOIN quiz_questions qq ON qq.id = qa.question_id
                ORDER BY qa.attempted_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_dashboard_stats(self):
        with get_connection() as connection:
            totals = connection.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM students) AS students,
                    (SELECT COUNT(*) FROM instructors) AS instructors,
                    (SELECT COUNT(*) FROM courses) AS courses,
                    (SELECT COUNT(*) FROM enrollments WHERE payment_status = 'Pagado') AS paid_enrollments,
                    (SELECT COUNT(*) FROM enrollments WHERE completed = 1) AS completed_enrollments,
                    (SELECT COALESCE(SUM(c.price), 0)
                     FROM enrollments e
                     JOIN courses c ON c.id = e.course_id
                     WHERE e.payment_status = 'Pagado') AS revenue,
                    (SELECT COUNT(*) FROM materials) AS materials_count,
                    (SELECT CASE
                         WHEN COUNT(*) = 0 THEN 0
                         ELSE CAST(ROUND(COUNT(CASE WHEN completed = 1 THEN 1 END) * 100.0 / COUNT(*)) AS INTEGER)
                     END FROM enrollments) AS completion_rate
                """
            ).fetchone()
            instructor_panel = connection.execute(
                """
                SELECT i.name,
                       COUNT(DISTINCT e.student_id) AS active_students,
                       COALESCE(SUM(CASE WHEN e.payment_status = 'Pagado' THEN c.price ELSE 0 END), 0) AS revenue
                FROM instructors i
                LEFT JOIN courses c ON c.instructor_id = i.id
                LEFT JOIN enrollments e ON e.course_id = c.id
                GROUP BY i.id, i.name
                ORDER BY revenue DESC, active_students DESC
                """
            ).fetchall()
            top_students = connection.execute(
                """
                SELECT s.name,
                       COALESCE(SUM(qa.score), 0) AS total_pts,
                       COUNT(DISTINCT e.course_id) AS courses_count
                FROM students s
                LEFT JOIN enrollments e ON e.student_id = s.id
                LEFT JOIN quiz_attempts qa ON qa.enrollment_id = e.id
                GROUP BY s.id, s.name
                ORDER BY total_pts DESC, courses_count DESC
                LIMIT 4
                """
            ).fetchall()
        return dict(totals), [dict(row) for row in instructor_panel], [dict(row) for row in top_students]
