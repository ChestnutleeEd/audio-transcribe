; Audio-Transcribe Windows 安装器配置
; 使用方式：
;   1. 在 Windows 构建机安装 Inno Setup。
;   2. 先运行 scripts\build-release.ps1 -Version v1.0.0 -Target installer-windows。
;   3. 脚本会调用 ISCC 生成 AudioTranscribeSetup.exe。

#define MyAppName "Audio-Transcribe"
#define MyAppVersion GetEnv("AUDIO_TRANSCRIBE_VERSION")
#define MyAppPublisher "Audio-Transcribe"
#define MyAppExeName "start-audio-transcribe.bat"
#define MySourceDir GetEnv("AUDIO_TRANSCRIBE_WINDOWS_STAGE")
#define MyOutputDir GetEnv("AUDIO_TRANSCRIBE_WINDOWS_INSTALLER_DIR")
#define MyLanguageFile GetEnv("AUDIO_TRANSCRIBE_INNO_LANGUAGE_FILE")

[Setup]
AppId={{8D0E0C49-EC5B-4A9D-83C7-A1B4D5D50C8E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Audio-Transcribe
DefaultGroupName=Audio-Transcribe
DisableProgramGroupPage=yes
OutputDir={#MyOutputDir}
OutputBaseFilename=AudioTranscribeSetup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName=Audio-Transcribe
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "chinesesimp"; MessagesFile: "{#MyLanguageFile}"

[Messages]
WelcomeLabel1=欢迎安装 Audio-Transcribe
WelcomeLabel2=本向导将把 Audio-Transcribe 安装到你的电脑，并创建桌面快捷方式。
FinishedHeadingLabel=Audio-Transcribe 安装完成
FinishedLabel=安装已经完成。你可以从桌面快捷方式或开始菜单启动 Audio-Transcribe。

[Files]
Source: "{#MySourceDir}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\Audio-Transcribe"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{userdesktop}\Audio-Transcribe"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式："; Flags: checkedonce

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "启动 Audio-Transcribe"; Flags: nowait postinstall skipifsilent
