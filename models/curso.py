class Curso:
    def __init__(self, nombre, instructor):
        self.nombre = nombre
        self.instructor = instructor
        self.estudiantes = []

    def inscribir_estudiante(self, estudiante):
        self.estudiantes.append(estudiante)