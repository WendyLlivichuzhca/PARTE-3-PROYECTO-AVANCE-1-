# Pruebas del instalador de EduCampus

## Objetivo
Verificar que el instalador de EduCampus permita instalar y ejecutar correctamente la aplicacion en Windows.

## Herramientas utilizadas
- PyInstaller para generar el ejecutable.
- Inno Setup 6 para construir el instalador.
- unittest para pruebas basicas de logica.
- Pruebas manuales funcionales sobre el instalador y la aplicacion instalada.

## Casos de prueba ejecutados

| ID | Prueba | Pasos | Resultado esperado |
|---|---|---|---|
| 1 | Apertura del instalador | Ejecutar `Setup_EduCampus.exe` | El asistente de instalacion inicia sin errores |
| 2 | Instalacion completa | Seguir el asistente hasta finalizar | La aplicacion se instala correctamente |
| 3 | Acceso directo | Marcar la opcion de escritorio y finalizar instalacion | Se crea el acceso directo de EduCampus |
| 4 | Inicio de la aplicacion | Abrir EduCampus desde el menu Inicio o escritorio | La interfaz principal abre correctamente |
| 5 | Persistencia de datos | Registrar instructor, estudiante y curso | Los datos quedan almacenados en SQLite |
| 6 | Inscripcion y pago | Crear una inscripcion y registrar pago | El estado de pago se actualiza correctamente |
| 7 | Certificado PDF | Completar una inscripcion al 100% y generar certificado | Se crea el archivo PDF en la carpeta de certificados |
| 8 | Descarga de materiales | Abrir un material PDF o documento desde la aplicacion | El archivo se descarga en la carpeta de materiales |
| 9 | Reapertura del sistema | Cerrar y volver a abrir EduCampus | La aplicacion mantiene su funcionamiento |

## Evidencia sugerida
- Captura del asistente de instalacion.
- Captura de la app instalada en ejecucion.
- Captura de la base de datos o registros creados.
- Captura del certificado PDF generado.
- Captura de la carpeta de materiales descargados.

## Resultado global
Si todos los casos anteriores se cumplen, el instalador se considera valido para la entrega academica.
