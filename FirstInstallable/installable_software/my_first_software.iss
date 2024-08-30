[Setup]
AppName=My First Installable Software
AppVersion=1.0
DefaultDirName={pf}\MyFirstSoftware
DefaultGroupName=My First Software
UninstallDisplayIcon={app}\main.exe
OutputDir=.
OutputBaseFilename=setup_my_first_software
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autodesktop}\My First Software"; Filename: "{app}\main.exe"; WorkingDir: "{app}"
Name: "{group}\My First Software"; Filename: "{app}\main.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\main.exe"; Description: "Launch My First Software"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
