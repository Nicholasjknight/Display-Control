[Setup]
AppName=Display Control+ Professional Edition
AppVersion=1.0.0
AppVerName=Display Control+ Professional Edition v1.0.0
AppPublisher=DisplayControl Solutions
AppPublisherURL=https://displaycontrolplus.com
AppSupportURL=https://displaycontrolplus.com/support
AppUpdatesURL=https://displaycontrolplus.com/updates
AppCopyright=Copyright © 2025 DisplayControl Solutions. All rights reserved.
DefaultDirName={autopf}\DisplayControlPlus
DefaultGroupName=Display Control+ Professional
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt
OutputDir=installer_output
OutputBaseFilename=DisplayControlPlus_Professional_Setup_v1.0.0
SetupIconFile=Display Control+ Logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no
ShowLanguageDialog=no
LanguageDetectionMethod=locale
UninstallDisplayIcon={app}\DisplayControlPlus.exe
UninstallDisplayName=Display Control+ Professional Edition
VersionInfoVersion=1.0.0.0
VersionInfoCompany=DisplayControl Solutions
VersionInfoDescription=Professional OLED Screen Protection Software
VersionInfoCopyright=Copyright © 2025 DisplayControl Solutions
VersionInfoProductName=Display Control+ Professional Edition
VersionInfoProductVersion=1.0.0
MinVersion=10.0
ArchitecturesAllowed=x64 arm64
ArchitecturesInstallIn64BitMode=x64 arm64
PrivilegesRequired=admin
RestartIfNeededByRun=no

; Code signing (uncomment when certificate is available)
; SignTool=standard
; SignedUninstaller=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "startupentry"; Description: "Start automatically with Windows (recommended)"; GroupDescription: "Startup options"; Flags: checkablealone checked
Name: "startmenuentry"; Description: "Add to Start Menu"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone checked

[Files]
; Main application files
Source: "dist\DisplayControlPlus\DisplayControlPlus.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\DisplayControlPlus\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "update_manager.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "version.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "Display Control+ Logo.png"; DestDir: "{app}"; Flags: ignoreversion
Source: "Display Control+ Logo.ico"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "COMMERCIAL_GUIDE.md"; DestDir: "{app}"; Flags: ignoreversion

; Assets (if they exist)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{group}\Display Control+ Professional"; Filename: "{app}\DisplayControlPlus.exe"; IconFilename: "{app}\Display Control+ Logo.ico"
Name: "{group}\{cm:UninstallProgram,Display Control+ Professional}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Display Control+ Professional"; Filename: "{app}\DisplayControlPlus.exe"; IconFilename: "{app}\Display Control+ Logo.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Display Control+ Professional"; Filename: "{app}\DisplayControlPlus.exe"; IconFilename: "{app}\Display Control+ Logo.ico"; Tasks: quicklaunchicon

[Registry]
; Auto-start entry (if selected)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "DisplayControlPlus"; ValueData: """{app}\DisplayControlPlus.exe"" --background"; Tasks: startupentry

[Run]
; Option to launch application after installation
Filename: "{app}\DisplayControlPlus.exe"; Description: "{cm:LaunchProgram,Display Control+ Professional}"; Flags: nowait postinstall skipifsilent unchecked

[UninstallRun]
; Stop any running processes before uninstall
Filename: "{cmd}"; Parameters: "/c taskkill /f /im DisplayControlPlus.exe"; Flags: runhidden; RunOnceId: "StopDisplayControlPlus"

[UninstallDelete]
; Clean up log files and user data
Type: files; Name: "{app}\overlay.log"
Type: files; Name: "{app}\update.log"
Type: files; Name: "{app}\*.tmp"

[Code]
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;

function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);
  
  // Check Windows version (Windows 10 or later required)
  if Version.Major < 10 then
  begin
    MsgBox('Display Control+ Professional requires Windows 10 or later.' + #13#10 + 
           'Your Windows version is not supported.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  Result := True;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  // Custom page styling could go here
end;
