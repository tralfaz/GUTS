#NSIS Example Install Script

#Basic definitions
!define APPNAME "Guts"
!define COMPANYNAME "MiDoMa"
!define DESCRIPTION "N-Body Gravity Simulation"
!define APPSHORTNAME "Guts"

!define VERSIONMAJOR 0
!define VERSIONMINOR 8
!define VERSIONBUILD 3

!define HELPURL "https://github.com/tralfaz/GUTS" 
!define UPDATEURL "https://github.com/tralfaz/GUTS"
!define ABOUTURL "https://github.com/tralfaz/GUTS/blob/main/README.md"

#Ask for administrative rights
RequestExecutionLevel admin

#Other options include:
#none
#user
#highest

#Default installation location - let's clutter up our root directory!
InstallDir "C:\Program Files\${APPSHORTNAME}"

#Text (or RTF) file with license information. The text file must be in DOS end line format (\r\n)
LicenseData "license.txt"

#'Name' goes in the installer's title bar
Name "${COMPANYNAME}-${APPSHORTNAME}"

#Icon for the installer - this is the default icon
#Icon "dist/assets/vault-icon.ico"

#The following lines replace the default icons
!include "MUI2.nsh"

#The name of the installer executable
outFile "${APPSHORTNAME}-install.exe"

#...Not certain about this one
!include LogicLib.nsh

#Defines installation pages - these are known to NSIS
#Shows the license
Page license
#Allows user to pick install path
Page directory
#Installs the files
Page instfiles

#A macro to verify that administrator rights have been acquired
!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
        messageBox mb_iconstop "Administrator rights required!"
        setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
        quit
${EndIf}
!macroend

#This ensures the administrator check is performed at startup?
function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

# Files for the install directory - to build the installer, these should be in the same directory as the install script (this file)
section "install"
    setOutPath $INSTDIR
         
    # Files added here should be removed by the uninstaller (see section "uninstall")
    file /r dist\Guts\*.*
    CreateDirectory $INSTDIR\assets
    CopyFiles assets\vault-icon.ico $INSTDIR\assets
    file /oname=assets\guts-win-installer.ico assets\guts-win-installer.ico
                     
    # Add any other files for the install directory (license files, app data, etc) here
                     	 
    #This creates a shortcut to the executable on the desktop - the second set of options in quotes are for command-line arguments
    CreateShortcut "$desktop\GUTS.lnk" "$instdir\Guts.exe"

sectionEnd


# Uninstaller

function un.onInit
    SetShellVarContext all

    #Verify the uninstaller - last chance to back out
    MessageBox MB_OKCANCEL "Permanantly remove ${APPNAME}?" IDOK next
  	Abort
    next:
	!insertmacro VerifyUserIsAdmin
functionEnd

section "uninstall"

    # Remove Start Menu launcher
    delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
  	 						  			    # Try to remove the Start Menu folder - this will only happen if it is empty
    rmDir "$SMPROGRAMS\${COMPANYNAME}"

    # Remove files
    delete $INSTDIR\Guts.exe
    delete $INSTDIR\guts-win-installer.ico

    # Always delete uninstaller as the last action
    delete $INSTDIR\uninstall.exe

    # Try to remove the install directory - this will only happen if it is empty
    rmDir $INSTDIR

    # Remove uninstaller information from the registry
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"

sectionEnd
