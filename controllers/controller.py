from services.course_service import CourseService


class Controller:
    def __init__(self):
        self.service = CourseService()

    def create_instructor(self, name, specialty):
        self.service.create_instructor(name, specialty)

    def create_student(self, name, age, email):
        self.service.create_student(name, age, email)

    def create_course(self, name, category, level, instructor_id, price, description):
        self.service.create_course(
            name, category, level, instructor_id, price, description
        )

    def create_enrollment(self, student_id, course_id, payment_status):
        self.service.create_enrollment(student_id, course_id, payment_status)

    def update_progress(self, enrollment_id, progress):
        self.service.update_progress(enrollment_id, progress)

    def register_payment(self, enrollment_id):
        self.service.register_payment(enrollment_id)

    def generate_certificate(self, enrollment_id):
        return self.service.generate_certificate_for_enrollment(enrollment_id)

    def create_material(self, course_id, title, url, material_type):
        self.service.create_material(course_id, title, url, material_type)

    def create_forum_message(
        self, course_id, sender_type, message, student_id=None, instructor_id=None
    ):
        self.service.create_forum_message(
            course_id, sender_type, message, student_id, instructor_id
        )

    def create_quiz_question(
        self, course_id, question, option_a, option_b, option_c, option_d, correct_option
    ):
        self.service.create_quiz_question(
            course_id, question, option_a, option_b, option_c, option_d, correct_option
        )

    def submit_quiz_attempt(self, enrollment_id, question_id, selected_option):
        return self.service.submit_quiz_attempt(
            enrollment_id, question_id, selected_option
        )

    def create_review(self, course_id, student_id, rating, comment):
        self.service.create_review(course_id, student_id, rating, comment)

    def get_instructors(self):
        return self.service.get_instructors()

    def get_students(self):
        return self.service.get_students()

    def get_courses(self, level=None):
        return self.service.get_courses(level)

    def get_enrollments(self):
        return self.service.get_enrollments()

    def get_materials(self):
        return self.service.get_materials()

    def get_forum_messages(self):
        return self.service.get_forum_messages()

    def get_quiz_questions(self):
        return self.service.get_quiz_questions()

    def get_reviews(self):
        return self.service.get_reviews()

    def get_quiz_attempts(self):
        return self.service.get_quiz_attempts()

    def get_dashboard_stats(self):
        return self.service.get_dashboard_stats()
