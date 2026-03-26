$ErrorActionPreference = "Stop"

Write-Host "Instalando dependencias de construccion..."
python -m pip install -r requirements.txt

Write-Host "Generando ejecutable con PyInstaller..."
python -m PyInstaller --clean EduCampus.spec

Write-Host "Compilando instalador con Inno Setup..."
$innoCompiler = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"

if (-not (Test-Path $innoCompiler)) {
    $innoCompiler = "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
}

if (-not (Test-Path $innoCompiler)) {
    throw "No se encontro ISCC.exe. Instala Inno Setup 6 para generar el instalador."
}

& $innoCompiler "instalador_educampus.iss"

Write-Host "Proceso completado. Revisa la carpeta output."
