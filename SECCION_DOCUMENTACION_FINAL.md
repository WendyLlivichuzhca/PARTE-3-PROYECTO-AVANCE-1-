# Seccion para agregar al documento final

## Librerias y herramientas del proyecto

EduCampus fue desarrollado en Python para escritorio, usando una arquitectura modular basada en controladores, servicios, modelos y vistas. Las librerias y herramientas principales utilizadas fueron las siguientes:

- `customtkinter`: construccion de la interfaz grafica moderna.
- `tkinter`: componentes base de la interfaz.
- `sqlite3`: almacenamiento local de datos.
- `pathlib`: manejo de rutas y archivos.
- `urllib`: descarga de materiales desde enlaces web.
- `webbrowser`: apertura de recursos externos desde la aplicacion.
- `subprocess`: apertura de archivos locales descargados o generados.
- `PyInstaller`: generacion del ejecutable de escritorio.
- `Inno Setup 6`: construccion del instalador para Windows.
- `unittest`: ejecucion de pruebas basicas de logica y validaciones.

## Ciclo de pruebas

Para el ciclo de pruebas se consideraron dos tipos de validacion:

1. Pruebas automaticas

Se implementaron pruebas con `unittest` para validar reglas de negocio importantes, como:

- validacion de correo del estudiante;
- restriccion de inscripcion en cursos no disponibles;
- actualizacion del certificado en la inscripcion al completar el 100 por ciento del progreso.

2. Pruebas manuales del instalador

Se realizaron pruebas funcionales del instalador verificando:

- apertura correcta del asistente de instalacion;
- instalacion completa de la aplicacion;
- creacion del acceso directo;
- apertura del sistema instalado;
- persistencia de datos en SQLite;
- generacion de certificados PDF;
- descarga de materiales del curso.

## Conclusion

Con estas herramientas y pruebas se aseguro que EduCampus pueda ser distribuido como aplicacion instalable y que mantenga su funcionamiento principal despues del proceso de instalacion.
