"""
seed_data.py — Ejecuta este archivo para poblar la base de datos con datos reales.
Uso: python seed_data.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "sistema_cursos.db"

def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = OFF")

    # ── Limpiar tablas ─────────────────────────────────────────
    for t in ["reviews","quiz_attempts","quiz_questions","forum_messages",
              "materials","enrollments","courses","students","instructors"]:
        conn.execute(f"DELETE FROM {t}")
    conn.execute("DELETE FROM sqlite_sequence")
    conn.commit()
    print("✓ Tablas limpiadas")

    # ── INSTRUCTORES ───────────────────────────────────────────
    conn.executemany("INSERT INTO instructors(name, specialty) VALUES(?,?)", [
        ("Carlos Mendoza",    "Desarrollo Web"),
        ("Maria Torres",      "Ciencia de Datos"),
        ("Luis Paredes",      "Diseño UX/UI"),
        ("Ana Valeria Ruiz",  "Ciberseguridad"),
        ("Jorge Castillo",    "Inteligencia Artificial"),
    ])
    print("✓ 5 instructores insertados")

    # ── ESTUDIANTES ────────────────────────────────────────────
    conn.executemany("INSERT INTO students(name, age, email) VALUES(?,?,?)", [
        ("Sofia Almeida",    22, "sofia.almeida@gmail.com"),
        ("Diego Hernandez",  25, "diego.hernandez@hotmail.com"),
        ("Valentina Cruz",   20, "valentina.cruz@gmail.com"),
        ("Andres Vega",      28, "andres.vega@outlook.com"),
        ("Camila Morales",   23, "camila.morales@gmail.com"),
        ("Sebastian Rojas",  26, "sebastian.rojas@gmail.com"),
        ("Isabella Flores",  21, "isabella.flores@hotmail.com"),
        ("Miguel Sanchez",   30, "miguel.sanchez@gmail.com"),
        ("Gabriela Jimenez", 24, "gabriela.jimenez@outlook.com"),
        ("Daniel Vargas",    27, "daniel.vargas@gmail.com"),
        ("Lucia Perez",      22, "lucia.perez@gmail.com"),
        ("Mateo Cordova",    29, "mateo.cordova@hotmail.com"),
    ])
    print("✓ 12 estudiantes insertados")

    # ── CURSOS ─────────────────────────────────────────────────
    conn.executemany(
        "INSERT INTO courses(name,category,level,instructor_id,price,description,status) VALUES(?,?,?,?,?,?,?)", [
        ("Desarrollo Web con Python y Django","Programacion",    "Intermedio",1,149.99,"Aprende a construir aplicaciones web completas con Django.","Activo"),
        ("Machine Learning con Python",       "Ciencia de Datos","Avanzado",  2,199.99,"Domina los algoritmos de aprendizaje automatico con Python.","Activo"),
        ("Diseño UX/UI con Figma",            "Diseño",          "Basico",    3, 99.99,"Aprende a diseñar interfaces modernas con Figma.","Activo"),
        ("Ciberseguridad Etica",              "Seguridad",       "Intermedio",4,179.99,"Aprende tecnicas de hacking etico y proteccion de sistemas.","Activo"),
        ("Inteligencia Artificial Aplicada",  "IA",              "Avanzado",  5,229.99,"Implementa soluciones de IA con redes neuronales.","Activo"),
        ("HTML, CSS y JavaScript desde cero", "Programacion",    "Basico",    1, 79.99,"El curso completo para iniciar en desarrollo web frontend.","Activo"),
        ("Analisis de Datos con Pandas",      "Ciencia de Datos","Intermedio",2,129.99,"Manipula y visualiza datos con Pandas.","Activo"),
        ("React JS para Principiantes",       "Programacion",    "Basico",    1, 89.99,"Crea aplicaciones web dinamicas con React.","Activo"),
    ])
    print("✓ 8 cursos insertados")
    conn.commit()

    # ── INSCRIPCIONES ──────────────────────────────────────────
    conn.executemany(
        "INSERT INTO enrollments(student_id,course_id,progress,payment_status,completed) VALUES(?,?,?,?,?)", [
        (1,1,100,"Pagado",1),(1,6,75,"Pagado",0),
        (2,2,60,"Pagado",0),(2,5,40,"Pagado",0),
        (3,3,100,"Pagado",1),(3,8,55,"Pagado",0),
        (4,4,80,"Pagado",0),(4,1,100,"Pagado",1),
        (5,2,90,"Pagado",0),(5,7,70,"Pagado",0),
        (6,5,45,"Pagado",0),(6,6,100,"Pagado",1),
        (7,3,65,"Pagado",0),(7,8,30,"Pendiente",0),
        (8,4,85,"Pagado",0),(8,2,100,"Pagado",1),
        (9,1,50,"Pagado",0),(9,7,20,"Pendiente",0),
        (10,5,75,"Pagado",0),(10,3,100,"Pagado",1),
        (11,6,90,"Pagado",0),(11,4,55,"Pagado",0),
        (12,8,100,"Pagado",1),(12,2,40,"Pagado",0),
    ])
    print("✓ 24 inscripciones insertadas")

    # ── MATERIALES ─────────────────────────────────────────────
    conn.executemany(
        "INSERT INTO materials(course_id,title,url,material_type) VALUES(?,?,?,?)", [
        (1,"Introduccion a Django",         "https://docs.djangoproject.com",            "Documento"),
        (1,"Video: Instalacion del entorno","https://youtube.com/watch?v=django-setup",  "Video"),
        (1,"Guia de modelos y ORM",         "https://docs.djangoproject.com/models",     "PDF"),
        (1,"Repositorio del curso",         "https://github.com/educampus/django-curso", "Repositorio"),
        (2,"Introduccion a Machine Learning","https://scikit-learn.org/stable/",         "Documento"),
        (2,"Video: Regresion Lineal",       "https://youtube.com/watch?v=ml-lineal",     "Video"),
        (2,"Dataset de practica - Kaggle",  "https://kaggle.com/datasets/iris",          "Repositorio"),
        (3,"Principios de Diseño UX",       "https://uxdesign.cc/principles",            "PDF"),
        (3,"Video: Figma desde cero",       "https://youtube.com/watch?v=figma-intro",   "Video"),
        (3,"Plantillas Figma Community",    "https://figma.com/community/educampus",     "Repositorio"),
        (4,"Manual de Hacking Etico OWASP", "https://owasp.org/guide",                  "PDF"),
        (4,"Video: OWASP Top 10",           "https://youtube.com/watch?v=owasp-top10",   "Video"),
        (5,"Fundamentos de IA - Google",    "https://ai.google/education",              "Documento"),
        (5,"Video: Redes Neuronales",       "https://youtube.com/watch?v=nn-intro",      "Video"),
        (5,"Repositorio TensorFlow",        "https://github.com/tensorflow/tensorflow",  "Repositorio"),
        (6,"Guia HTML5 - MDN Web Docs",     "https://developer.mozilla.org/html",       "Documento"),
        (6,"Video: CSS Flexbox y Grid",     "https://youtube.com/watch?v=css-flex",      "Video"),
        (6,"Ejercicios JavaScript",         "https://javascript.info",                  "PDF"),
        (7,"Documentacion oficial Pandas",  "https://pandas.pydata.org/docs",           "Documento"),
        (7,"Video: DataFrames y Series",    "https://youtube.com/watch?v=pandas-intro",  "Video"),
        (8,"Documentacion React",           "https://react.dev",                        "Documento"),
        (8,"Video: Hooks en React",         "https://youtube.com/watch?v=react-hooks",   "Video"),
        (8,"Repositorio ejemplos React",    "https://github.com/educampus/react-demos", "Repositorio"),
    ])
    print("✓ 23 materiales insertados")

    # ── FORO ───────────────────────────────────────────────────
    conn.executemany(
        "INSERT INTO forum_messages(course_id,sender_type,message,student_id,instructor_id) VALUES(?,?,?,?,?)", [
        (1,"instructor","Bienvenidos al curso de Django! Revisen los materiales antes de cada clase.",None,1),
        (1,"student",   "Hola profe, como defino relaciones ManyToMany en los modelos?",1,None),
        (1,"instructor","Hola Sofia! Se usa ManyToManyField. Lo vemos en el modulo 3.",None,1),
        (2,"instructor","Iniciamos con regresion lineal. Descarguen el dataset de Materiales.",None,2),
        (2,"student",   "El dataset tiene valores nulos, como los manejo antes de entrenar?",2,None),
        (3,"instructor","Para el primer proyecto necesitan cuenta en figma.com (es gratuita).",None,3),
        (3,"student",   "Se puede exportar el diseño directamente a codigo CSS?",3,None),
        (4,"instructor","Todo lo aprendido aqui es exclusivamente para uso etico y legal.",None,4),
        (5,"student",   "Increible el tema de redes neuronales! Que recursos extras recomiendas?",5,None),
        (6,"instructor","Empezamos con HTML semantico, fundamental para accesibilidad y SEO.",None,1),
        (6,"student",   "Complete el modulo 1! Los ejercicios de JavaScript estan muy bien.",6,None),
        (8,"instructor","React es una libreria, no un framework. Esa diferencia es clave.",None,1),
        (7,"student",   "Como manejo datos faltantes con Pandas?",9,None),
        (7,"instructor","Usa df.fillna() o df.dropna() segun el caso. Lo vemos en modulo 2.",None,2),
    ])
    print("✓ 14 mensajes de foro insertados")

    # ── PREGUNTAS QUIZ ─────────────────────────────────────────
    conn.executemany(
        "INSERT INTO quiz_questions(course_id,question,option_a,option_b,option_c,option_d,correct_option) VALUES(?,?,?,?,?,?,?)", [
        (1,"Cual es el comando para crear un proyecto Django?","django-admin startproject","python manage.py startapp","pip install django","django create project","A"),
        (1,"Que archivo contiene la configuracion principal en Django?","urls.py","models.py","settings.py","views.py","C"),
        (1,"Como se llama el ORM integrado de Django?","SQLAlchemy","Django ORM","Peewee","Tortoise","B"),
        (2,"Cual algoritmo se usa para clasificacion binaria?","Regresion Lineal","K-Means","Regresion Logistica","PCA","C"),
        (2,"Que libreria Python es la mas usada para ML clasico?","TensorFlow","Scikit-learn","Keras","PyTorch","B"),
        (3,"Que significa UX?","User eXperience","User eXpert","Unique eXperience","User eXchange","A"),
        (3,"Cual herramienta usamos para prototipado en este curso?","Adobe XD","Sketch","Figma","InVision","C"),
        (4,"En que consiste SQL Injection?","Un tipo de virus","Insercion maliciosa de SQL en formularios","Backup de BD","Encriptacion","B"),
        (4,"Cual es el puerto por defecto de HTTPS?","80","8080","443","21","C"),
        (5,"Que es una red neuronal artificial?","Un tipo de BD","Un modelo inspirado en el cerebro humano","Un algoritmo de busqueda","Un protocolo","B"),
        (6,"Que etiqueta define el titulo principal visible de una pagina?","<title>","<h1>","<header>","<main>","B"),
        (6,"Como se enlaza un archivo CSS externo correctamente?","<style src=...>","<css href=...>","<link rel=stylesheet href=...>","<import css=...>","C"),
        (8,"Que hook se usa para manejar estado local en React?","useEffect","useRef","useState","useContext","C"),
        (8,"Cual es la forma moderna de montar React en el DOM?","React.render()","ReactDOM.createRoot()","React.mount()","ReactDOM.render()","B"),
    ])
    print("✓ 14 preguntas de quiz insertadas")

    # ── INTENTOS QUIZ ──────────────────────────────────────────
    conn.executemany(
        "INSERT INTO quiz_attempts(enrollment_id,question_id,selected_option,score,status) VALUES(?,?,?,?,?)", [
        (1,1,"A",10,"Aprobado"),(1,2,"C",10,"Aprobado"),(1,3,"B",10,"Aprobado"),
        (3,4,"C",10,"Aprobado"),(3,5,"B",10,"Aprobado"),
        (5,6,"A",10,"Aprobado"),(5,7,"C",10,"Aprobado"),
        (7,8,"B",10,"Aprobado"),(7,9,"A",0,"Reprobado"),
        (8,1,"A",10,"Aprobado"),(8,2,"C",10,"Aprobado"),
        (9,4,"C",10,"Aprobado"),(9,5,"A",0,"Reprobado"),
        (11,10,"B",10,"Aprobado"),
        (13,6,"A",10,"Aprobado"),(13,7,"B",0,"Reprobado"),
        (15,8,"B",10,"Aprobado"),(15,9,"C",10,"Aprobado"),
        (19,10,"B",10,"Aprobado"),
        (21,11,"B",10,"Aprobado"),(21,12,"C",10,"Aprobado"),
        (23,13,"C",10,"Aprobado"),(23,14,"B",10,"Aprobado"),
    ])
    print("✓ 23 intentos de quiz insertados")

    # ── RESEÑAS ────────────────────────────────────────────────
    conn.executemany(
        "INSERT INTO reviews(course_id,student_id,rating,comment) VALUES(?,?,?,?)", [
        (1,1,5,"Excelente curso! Carlos explica muy bien y los proyectos son practicos."),
        (1,4,5,"El mejor curso de Django que he tomado. Lo recomiendo al 100%."),
        (2,2,4,"Muy buen contenido sobre ML. Me gustaria mas ejercicios practicos."),
        (2,8,5,"Maria es una experta. Ya aplico ML en mi trabajo gracias a este curso."),
        (3,3,5,"Aprendi Figma desde cero en pocas semanas. Luis es increible."),
        (3,10,4,"Buen curso de UX. Los recursos son muy utiles para el trabajo."),
        (4,4,5,"El curso de ciberseguridad supero mis expectativas. Muy completo."),
        (5,5,4,"Increible el contenido de IA. Quiero el nivel avanzado!"),
        (6,6,4,"HTML/CSS/JS bien explicado para principiantes. Muy recomendado."),
        (6,12,5,"Perfecto para empezar en web. Ya tengo mi primer proyecto!"),
        (8,12,5,"React explicado de manera clara y con proyectos reales. Excelente."),
    ])
    print("✓ 11 reseñas insertadas")

    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()

    print("\n=== RESUMEN ===")
    for t in ["instructors","students","courses","enrollments","materials",
              "forum_messages","quiz_questions","quiz_attempts","reviews"]:
        c = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:22s}: {c:3d} registros")

    conn.close()
    print("\n✅ Base de datos poblada exitosamente!")
    print(f"   Archivo: {DB_PATH}")

if __name__ == "__main__":
    seed()
