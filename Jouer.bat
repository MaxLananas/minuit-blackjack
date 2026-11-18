@echo off
setlocal DisableDelayedExpansion
cd /d "%~dp0"
set "PY=%CD%\python\python.exe"

if not exist "%PY%" goto runtime_absent
if not exist "%CD%\python\Lib\moteur.zip" goto incomplet
if not exist "%CD%\python\Lib\site-packages\ursina\__init__.py" goto incomplet

echo Lancement de la table...
if defined TEMP (
    "%PY%" -u -X "pycache_prefix=%TEMP%\Minuit-cache" "%CD%\minuit.py"
) else (
    "%PY%" -u -B "%CD%\minuit.py"
)
if not "%errorlevel%"=="0" goto erreur
exit /b 0

:runtime_absent
echo.
echo Le Python fourni avec le jeu est introuvable.
echo Extrayez TOUT le ZIP Windows, puis relancez Jouer.bat.
echo Le ZIP des sources seul ne contient pas le Python du jeu.
echo.
pause
exit /b 1

:incomplet
echo.
echo Des composants du jeu sont manquants.
echo Extrayez a nouveau TOUT le ZIP Windows dans un nouveau dossier.
echo.
pause
exit /b 1

:erreur
echo.
echo Le jeu s'est arrete avec une erreur. Gardez cette fenetre ouverte
echo et envoyez une capture du message ci-dessus pour obtenir de l'aide.
echo.
pause
exit /b 1
