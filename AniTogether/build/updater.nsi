; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "AniTogether"
!define PRODUCT_VERSION "1.0.0-alpha.6"
!define PRODUCT_PUBLISHER "AlexDev505"
!define PRODUCT_WEB_SITE "https://github.com/AlexDev505/AniTogether"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\AniTogether.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma
AutoCloseWindow true

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "sources\icon.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Instfiles page
!insertmacro MUI_PAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "Russian"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME}"
OutFile "updaters\AniTogetherUpdate ${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\AniTogether"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show

!define IfFileLocked "!insertmacro _IfFileLocked"

!macro _IfFileLocked label
  ClearErrors
  FileOpen $0 "$INSTDIR\AniTogether.exe" w
  IfErrors ${label}
  FileClose $0
!macroend

Section "AniTogether" SEC01
  SetOutPath "$INSTDIR"
  FileIsLocked:
    ${IfFileLocked} FileLocked
    File "AniTogether\AniTogether.exe"
    Goto Done
  FileLocked:
    Goto FileIsLocked
  Done:
SectionEnd

Section -Post
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
SectionEnd

Function .OnInstSuccess
  SetOutPath "$INSTDIR"
  Exec "AniTogether.exe"
FunctionEnd
