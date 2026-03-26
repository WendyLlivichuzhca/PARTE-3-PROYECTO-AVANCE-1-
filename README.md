# EduCampus - Sistema de Cursos Online

EduCampus es una aplicacion de escritorio desarrollada en Python para la gestion academica de cursos, estudiantes, instructores, materiales y evaluaciones. El proyecto sigue una arquitectura modular tipo MVC y utiliza SQLite para la persistencia local de datos.

## Caracteristicas principales

- Panel principal con estadisticas generales del sistema.
- Gestion de instructores, estudiantes, cursos e inscripciones.
- Seguimiento del progreso y control de pagos.
- Generacion automatica de certificados en PDF.
- Biblioteca de materiales con apertura o descarga de recursos.
- Foro, evaluaciones y resenas del curso.

## Tecnologias utilizadas

- Python 3
- CustomTkinter
- Tkinter
- SQLite3
- unittest
- PyInstaller
- Inno Setup 6

## Estructura del proyecto

- `controllers/`: coordinacion entre interfaz y servicios.
- `database/`: conexion SQLite y creacion del esquema.
- `models/`: entidades del dominio.
- `services/`: reglas de negocio del sistema.
- `utils/`: utilidades auxiliares, PDF y rutas de aplicacion.
- `views/`: interfaz grafica del sistema.
- `tests/`: pruebas basicas automatizadas.
- `docs/`: apoyo documental para pruebas e informe final.

## Ejecucion en desarrollo

1. Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

2. Ejecutar la aplicacion:

```powershell
python main.py
```

## Pruebas automatizadas

Ejecutar:

```powershell
python -m unittest discover -s tests
```

## Generacion del ejecutable

Ejecutar:

```powershell
python -m PyInstaller --clean EduCampus.spec
```

El ejecutable se genera en la carpeta `dist/EduCampus/`.

## Generacion del instalador

1. Instalar Inno Setup 6.
2. Abrir el archivo `instalador_educampus.iss`.
3. Compilar el script desde Inno Setup.

Tambien puedes usar:

```powershell
.\build_installer.ps1
```

El instalador final se genera en la carpeta `output/`.

## Pruebas del instalador

Las pruebas funcionales sugeridas del instalador estan documentadas en:

- `docs/PRUEBAS_INSTALADOR.md`

## Documentacion final

La seccion lista para pegar en el informe final se encuentra en:

- `docs/SECCION_DOCUMENTACION_FINAL.md`

## Nota tecnica importante

Cuando la aplicacion se ejecuta instalada, guarda la base de datos, certificados y materiales descargados en una carpeta escribible del usuario para evitar problemas de permisos en Windows.

Desarrollado para el curso de POO II.
