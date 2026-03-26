[Setup]
AppName=EduCampus
AppVersion=1.0
AppPublisher=Wendy Llivichuzhca
DefaultDirName={localappdata}\EduCampus
DefaultGroupName=EduCampus
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=Setup_EduCampus
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Files]
Source: "dist\EduCampus\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\EduCampus"; Filename: "{app}\EduCampus.exe"
Name: "{autodesktop}\EduCampus"; Filename: "{app}\EduCampus.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; Flags: unchecked

[Run]
Filename: "{app}\EduCampus.exe"; Description: "Ejecutar EduCampus"; Flags: nowait postinstall skipifsilent
