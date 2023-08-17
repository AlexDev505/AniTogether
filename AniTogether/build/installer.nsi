; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "AniTogether"
!define PRODUCT_VERSION "1.0.0-alpha.5"
!define PRODUCT_PUBLISHER "AlexDev505"
!define PRODUCT_WEB_SITE "https://github.com/AlexDev505/AniTogether"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\AniTogether.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "sources\icon.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\orange-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE "..\..\LICENCE"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\AniTogether.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "Russian"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME}"
OutFile "installers\AniTogetherSetup ${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\AniTogether"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "AniTogether" SEC01
  SetOverwrite try
  SetOutPath "$INSTDIR"
  File "AniTogether\AniTogether.exe"
  File "AniTogether\base_library.zip"
  File "AniTogether\libcrypto-1_1.dll"
  File "AniTogether\libffi-7.dll"
  File "AniTogether\libssl-1_1.dll"
  File "AniTogether\pyexpat.pyd"
  File "AniTogether\python310.dll"
  File "AniTogether\select.pyd"
  File "AniTogether\unicodedata.pyd"
  File "AniTogether\VCRUNTIME140.dll"
  File "AniTogether\_asyncio.pyd"
  File "AniTogether\_bz2.pyd"
  File "AniTogether\_cffi_backend.cp310-win_amd64.pyd"
  File "AniTogether\_ctypes.pyd"
  File "AniTogether\_decimal.pyd"
  File "AniTogether\_elementtree.pyd"
  File "AniTogether\_hashlib.pyd"
  File "AniTogether\_lzma.pyd"
  File "AniTogether\_multiprocessing.pyd"
  File "AniTogether\_overlapped.pyd"
  File "AniTogether\_queue.pyd"
  File "AniTogether\_socket.pyd"
  File "AniTogether\_ssl.pyd"
  File "AniTogether\_uuid.pyd"
  File "AniTogether\_zoneinfo.pyd"
  SetOutPath "$INSTDIR\certifi"
  File "AniTogether\certifi\cacert.pem"
  File "AniTogether\certifi\py.typed"
  SetOutPath "$INSTDIR\charset_normalizer"
  File "AniTogether\charset_normalizer\md.cp310-win_amd64.pyd"
  File "AniTogether\charset_normalizer\md__mypyc.cp310-win_amd64.pyd"
  SetOutPath "$INSTDIR\clr_loader\ffi\dlls\amd64"
  File "AniTogether\clr_loader\ffi\dlls\amd64\ClrLoader.dll"
  SetOutPath "$INSTDIR\clr_loader\ffi\dlls\x86"
  File "AniTogether\clr_loader\ffi\dlls\x86\ClrLoader.dll"
  SetOutPath "$INSTDIR\markupsafe"
  File "AniTogether\markupsafe\_speedups.cp310-win_amd64.pyd"
  SetOutPath "$INSTDIR\orjson"
  File "AniTogether\orjson\orjson.cp310-win_amd64.pyd"
  SetOutPath "$INSTDIR\pythonnet\runtime"
  File "AniTogether\pythonnet\runtime\Python.Runtime.dll"
  SetOutPath "$INSTDIR\static\css"
  File "AniTogether\static\css\base.css"
  File "AniTogether\static\css\home.css"
  File "AniTogether\static\css\overlays.css"
  File "AniTogether\static\css\player.css"
  SetOutPath "$INSTDIR\static\images"
  File "AniTogether\static\images\about.svg"
  File "AniTogether\static\images\circle.svg"
  File "AniTogether\static\images\cross.svg"
  File "AniTogether\static\images\crown.svg"
  File "AniTogether\static\images\go.svg"
  File "AniTogether\static\images\group.svg"
  File "AniTogether\static\images\home.svg"
  File "AniTogether\static\images\line.svg"
  File "AniTogether\static\images\loading.gif"
  File "AniTogether\static\images\muted.svg"
  File "AniTogether\static\images\no_muted.svg"
  File "AniTogether\static\images\pause_request.svg"
  File "AniTogether\static\images\person.svg"
  File "AniTogether\static\images\play.svg"
  File "AniTogether\static\images\playlist.svg"
  File "AniTogether\static\images\resolution_fhd.svg"
  File "AniTogether\static\images\resolution_hd.svg"
  File "AniTogether\static\images\resolution_sd.svg"
  File "AniTogether\static\images\rewind_request.svg"
  File "AniTogether\static\images\synchronize.svg"
  File "AniTogether\static\images\window.svg"
  SetOutPath "$INSTDIR\static\js"
  File "AniTogether\static\js\base.js"
  File "AniTogether\static\js\home.js"
  File "AniTogether\static\js\overlays.js"
  File "AniTogether\static\js\player.js"
  SetOutPath "$INSTDIR\templates"
  File "AniTogether\templates\base.html"
  File "AniTogether\templates\home.html"
  File "AniTogether\templates\player.html"
  SetOutPath "$INSTDIR\webview\lib"
  File "AniTogether\webview\lib\Microsoft.Web.WebView2.Core.dll"
  File "AniTogether\webview\lib\Microsoft.Web.WebView2.WinForms.dll"
  File "AniTogether\webview\lib\WebBrowserInterop.x64.dll"
  File "AniTogether\webview\lib\WebBrowserInterop.x86.dll"
  SetOutPath "$INSTDIR\webview\lib\runtimes\win-arm64\native"
  File "AniTogether\webview\lib\runtimes\win-arm64\native\WebView2Loader.dll"
  SetOutPath "$INSTDIR\webview\lib\runtimes\win-x64\native"
  File "AniTogether\webview\lib\runtimes\win-x64\native\WebView2Loader.dll"
  SetOutPath "$INSTDIR\webview\lib\runtimes\win-x86\native"
  File "AniTogether\webview\lib\runtimes\win-x86\native\WebView2Loader.dll"
  SetOutPath "$INSTDIR\wheel-0.41.1.dist-info"
  File "AniTogether\wheel-0.41.1.dist-info\entry_points.txt"
  File "AniTogether\wheel-0.41.1.dist-info\INSTALLER"
  File "AniTogether\wheel-0.41.1.dist-info\LICENSE.txt"
  File "AniTogether\wheel-0.41.1.dist-info\METADATA"
  File "AniTogether\wheel-0.41.1.dist-info\RECORD"
  File "AniTogether\wheel-0.41.1.dist-info\REQUESTED"
  File "AniTogether\wheel-0.41.1.dist-info\WHEEL"
  CreateShortCut "$SMPROGRAMS\AniTogether.lnk" "$INSTDIR\AniTogether.exe"
  CreateShortCut "$DESKTOP\AniTogether.lnk" "$INSTDIR\AniTogether.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\AniTogether.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\AniTogether.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "�������� ��������� $(^Name) ���� ������� ���������."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "�� ������� � ���, ��� ������� ������� $(^Name) � ��� ���������� ���������?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\uninst.exe"
  
  Delete "$INSTDIR\AniTogether.exe"
  Delete "$INSTDIR\base_library.zip"
  Delete "$INSTDIR\libcrypto-1_1.dll"
  Delete "$INSTDIR\libffi-7.dll"
  Delete "$INSTDIR\libssl-1_1.dll"
  Delete "$INSTDIR\pyexpat.pyd"
  Delete "$INSTDIR\python310.dll"
  Delete "$INSTDIR\select.pyd"
  Delete "$INSTDIR\unicodedata.pyd"
  Delete "$INSTDIR\VCRUNTIME140.dll"
  Delete "$INSTDIR\_asyncio.pyd"
  Delete "$INSTDIR\_bz2.pyd"
  Delete "$INSTDIR\_cffi_backend.cp310-win_amd64.pyd"
  Delete "$INSTDIR\_ctypes.pyd"
  Delete "$INSTDIR\_decimal.pyd"
  Delete "$INSTDIR\_elementtree.pyd"
  Delete "$INSTDIR\_hashlib.pyd"
  Delete "$INSTDIR\_lzma.pyd"
  Delete "$INSTDIR\_multiprocessing.pyd"
  Delete "$INSTDIR\_overlapped.pyd"
  Delete "$INSTDIR\_queue.pyd"
  Delete "$INSTDIR\_socket.pyd"
  Delete "$INSTDIR\_ssl.pyd"
  Delete "$INSTDIR\_uuid.pyd"
  Delete "$INSTDIR\_zoneinfo.pyd"
  Delete "$INSTDIR\certifi\cacert.pem"
  Delete "$INSTDIR\certifi\py.typed"
  Delete "$INSTDIR\charset_normalizer\md.cp310-win_amd64.pyd"
  Delete "$INSTDIR\charset_normalizer\md__mypyc.cp310-win_amd64.pyd"
  Delete "$INSTDIR\clr_loader\ffi\dlls\amd64\ClrLoader.dll"
  Delete "$INSTDIR\clr_loader\ffi\dlls\x86\ClrLoader.dll"
  Delete "$INSTDIR\markupsafe\_speedups.cp310-win_amd64.pyd"
  Delete "$INSTDIR\orjson\orjson.cp310-win_amd64.pyd"
  Delete "$INSTDIR\pythonnet\runtime\Python.Runtime.dll"
  Delete "$INSTDIR\static\css\base.css"
  Delete "$INSTDIR\static\css\home.css"
  Delete "$INSTDIR\static\css\overlays.css"
  Delete "$INSTDIR\static\css\player.css"
  Delete "$INSTDIR\static\images\about.svg"
  Delete "$INSTDIR\static\images\circle.svg"
  Delete "$INSTDIR\static\images\cross.svg"
  Delete "$INSTDIR\static\images\crown.svg"
  Delete "$INSTDIR\static\images\go.svg"
  Delete "$INSTDIR\static\images\group.svg"
  Delete "$INSTDIR\static\images\home.svg"
  Delete "$INSTDIR\static\images\line.svg"
  Delete "$INSTDIR\static\images\loading.gif"
  Delete "$INSTDIR\static\images\muted.svg"
  Delete "$INSTDIR\static\images\no_muted.svg"
  Delete "$INSTDIR\static\images\pause_request.svg"
  Delete "$INSTDIR\static\images\person.svg"
  Delete "$INSTDIR\static\images\play.svg"
  Delete "$INSTDIR\static\images\playlist.svg"
  Delete "$INSTDIR\static\images\resolution_fhd.svg"
  Delete "$INSTDIR\static\images\resolution_hd.svg"
  Delete "$INSTDIR\static\images\resolution_sd.svg"
  Delete "$INSTDIR\static\images\rewind_request.svg"
  Delete "$INSTDIR\static\images\synchronize.svg"
  Delete "$INSTDIR\static\images\window.svg"
  Delete "$INSTDIR\static\js\base.js"
  Delete "$INSTDIR\static\js\home.js"
  Delete "$INSTDIR\static\js\overlays.js"
  Delete "$INSTDIR\static\js\player.js"
  Delete "$INSTDIR\templates\base.html"
  Delete "$INSTDIR\templates\home.html"
  Delete "$INSTDIR\templates\player.html"
  Delete "$INSTDIR\webview\lib\Microsoft.Web.WebView2.Core.dll"
  Delete "$INSTDIR\webview\lib\Microsoft.Web.WebView2.WinForms.dll"
  Delete "$INSTDIR\webview\lib\WebBrowserInterop.x64.dll"
  Delete "$INSTDIR\webview\lib\WebBrowserInterop.x86.dll"
  Delete "$INSTDIR\webview\lib\runtimes\win-arm64\native\WebView2Loader.dll"
  Delete "$INSTDIR\webview\lib\runtimes\win-x64\native\WebView2Loader.dll"
  Delete "$INSTDIR\webview\lib\runtimes\win-x86\native\WebView2Loader.dll"
  Delete "$INSTDIR\wheel-0.41.1.dist-info\entry_points.txt"
  Delete "$INSTDIR\wheel-0.41.1.dist-info\INSTALLER"
  Delete "$INSTDIR\wheel-0.41.1.dist-info\LICENSE.txt"
  Delete "$INSTDIR\wheel-0.41.1.dist-info\METADATA"
  Delete "$INSTDIR\wheel-0.41.1.dist-info\RECORD"
  Delete "$INSTDIR\wheel-0.41.1.dist-info\REQUESTED"
  Delete "$INSTDIR\wheel-0.41.1.dist-info\WHEEL"

  RMDir "$INSTDIR\wheel-0.41.1.dist-info"
  RMDir "$INSTDIR\webview\lib\runtimes\win-x86\native"
  RMDir "$INSTDIR\webview\lib\runtimes\win-x86"
  RMDir "$INSTDIR\webview\lib\runtimes\win-x64\native"
  RMDir "$INSTDIR\webview\lib\runtimes\win-x64"
  RMDir "$INSTDIR\webview\lib\runtimes\win-arm64\native"
  RMDir "$INSTDIR\webview\lib\runtimes\win-arm64"
  RMDir "$INSTDIR\webview\lib\runtimes"
  RMDir "$INSTDIR\webview\lib"
  RMDir "$INSTDIR\webview"
  RMDir "$INSTDIR\templates"
  RMDir "$INSTDIR\static\js"
  RMDir "$INSTDIR\static\images"
  RMDir "$INSTDIR\static\css"
  RMDir "$INSTDIR\static"
  RMDir "$INSTDIR\pythonnet\runtime"
  RMDir "$INSTDIR\pythonnet"
  RMDir "$INSTDIR\orjson"
  RMDir "$INSTDIR\markupsafe"
  RMDir "$INSTDIR\clr_loader\ffi\dlls\x86"
  RMDir "$INSTDIR\clr_loader\ffi\dlls\amd64"
  RMDir "$INSTDIR\clr_loader\ffi\dlls"
  RMDir "$INSTDIR\clr_loader\ffi"
  RMDir "$INSTDIR\clr_loader"
  RMDir "$INSTDIR\charset_normalizer"
  RMDir "$INSTDIR\certifi"
  RMDir "$INSTDIR"

  Delete "$LocalAppData\AniTogether\debug.log"
  Delete "$LocalAppData\AniTogether\history.csv"
  RMDir "$LocalAppData"
  
  Delete "$DESKTOP\AniTogether.lnk"
  Delete "$SMPROGRAMS\AniTogether.lnk"
  
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd