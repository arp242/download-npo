#define MyAppName "download-npo"
#define MyAppVersion "2.2"
#define MyAppPublisher "Martin Tournoij"
#define MyAppURL "http://code.arp242.net/download-npo"
#define MyAppExeName "download-npo-gui.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{82BCB7AA-6967-4290-A366-A4770F847EAB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=download-npo-setup-{#MyAppVersion}
SetupIconFile=D:\icon.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "D:\dist_win32\download-npo-gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\dist_win32\download-npo.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "D:\dist_win32\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "D:\vcredist_x86.exe"; DestDir: {tmp}; Flags: deleteafterinstall 
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: {tmp}\vcredist_x86.exe; Parameters: "/q"; StatusMsg: Installing 2010 Runtime...

