@echo off
echo Script iniciado... Presiona una tecla para continuar.
pause
setlocal
echo Despues de setlocal. Presiona una tecla.
pause

REM --- Configuración ---
echo Configurando variables...
set "PROJECT_DIR=%CD%"
echo PROJECT_DIR set to %PROJECT_DIR%
set "NEW_PROJECT_NAME=mi-app-react"
echo NEW_PROJECT_NAME set to %NEW_PROJECT_NAME%
set "NODE_INSTALLER_URL=https://nodejs.org/dist/v18.18.0/node-v18.18.0-x64.msi"
echo NODE_INSTALLER_URL set
set "NODE_INSTALLER_NAME=node-installer.msi"
echo NODE_INSTALLER_NAME set
echo Fin de configuracion de variables. Presiona una tecla.
pause

REM --- Funciones Auxiliares (simuladas en Batch) ---

:check_command
echo Dentro de la etiqueta :check_command (antes de cualquier logica). Presiona una tecla.
pause
    REM Temporalmente comentado para depurar
    REM where %1 >nul 2>nul
    REM if %errorlevel% == 0 (
    REM     echo %1 encontrado.
    REM     exit /b 0
    REM ) else (
    REM     echo %1 no encontrado.
    REM     exit /b 1
    REM )
echo Fin de la etiqueta :check_command (logica comentada). Presiona una tecla.
pause
REM TODO EL CONTENIDO DESDE AQUÍ HA SIDO ELIMINADO PARA LA PRUEBA.
REM SI EL SCRIPT PERMANECE ABIERTO DESPUÉS DEL PAUSE ANTERIOR,
REM EL PROBLEMA ESTABA EN LA PRIMERA LÍNEA QUE SE ELIMINÓ.
REM echo Definiendo :install_node_npm. Presiona una tecla.
REM pause
    REM echo Intentando instalar Node.js y npm...
    REM echo Descargando instalador de Node.js...
    REM Usar PowerShell para descargar el archivo, ya que Batch no tiene un comando nativo simple.
    powershell -Command "(New-Object Net.WebClient).DownloadFile('%NODE_INSTALLER_URL%', '%NODE_INSTALLER_NAME%')"
    if errorlevel 1 (
        echo Error descargando Node.js. Por favor, instálalo manualmente desde nodejs.org.
        exit /b 1
    )

    echo Ejecutando instalador de Node.js...
    start /wait msiexec /i "%NODE_INSTALLER_NAME%" /quiet /norestart
    if errorlevel 1 (
        echo Error durante la instalacion de Node.js. Es posible que necesites ejecutar este script como administrador.
        del "%NODE_INSTALLER_NAME%" >nul 2>nul
        exit /b 1
    )
    del "%NODE_INSTALLER_NAME%" >nul 2>nul
    echo Node.js y npm deberian estar instalados. Por favor, abre una NUEVA ventana de terminal e intenta de nuevo.
    echo Es posible que necesites reiniciar tu sistema.
    REM Actualizar el PATH para la sesión actual (esto es complejo y no siempre funciona perfectamente sin reiniciar cmd)
    REM FOR /F "tokens=2*" %%A IN ('REG QUERY "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path') DO SET PATH=%%B
    echo Se recomienda abrir una nueva ventana de comandos para que los cambios en el PATH surtan efecto.
    REM exit /b 0

REM --- Flujo Principal ---

REM Comprobar Node.js
echo ANTES de llamar a :check_command node. Presiona una tecla.
pause
call :check_command node
echo DESPUES de llamar a :check_command node. Presiona una tecla.
pause
REM if errorlevel 1 (
    REM echo ANTES de llamar a :install_node_npm (rama errorlevel 1). Presiona una tecla.
    REM pause
    REM call :install_node_npm
    REM if errorlevel 1 (
        REM echo Instalacion de Node.js fallida. Saliendo.
        REM goto :eof
    REM )
    REM echo.
    REM echo POR FAVOR, CIERRA ESTA VENTANA DE COMANDOS Y ABRE UNA NUEVA.
    REM echo LUEGO, EJECUTA EL SCRIPT DE NUEVO EN LA NUEVA VENTANA.
    REM goto :eof
REM )

REM Comprobar npm
echo ANTES de llamar a :check_command npm. Presiona una tecla.
pause
call :check_command npm
echo DESPUES de llamar a :check_command npm. Presiona una tecla.
pause
REM if errorlevel 1 (
    REM echo npm no se encontro a pesar de que Node.js parece estar instalado.
    REM echo Esto es inusual. Intentando reinstalar Node.js y npm...
    REM call :install_node_npm
    REM if errorlevel 1 (
        REM echo Instalacion de Node.js/npm fallida. Saliendo.
        REM goto :eof
    REM )
    REM echo.
    REM echo POR FAVOR, CIERRA ESTA VENTANA DE COMANDOS Y ABRE UNA NUEVA.
    REM echo LUEGO, EJECUTA EL SCRIPT DE NUEVO EN LA NUEVA VENTANA.
    REM goto :eof
REM )

echo DESPUES de las comprobaciones de node y npm (condicionales comentadas). Presiona una tecla.
pause

REM set "PACKAGE_MANAGER=npm"
REM choice /C YN /M "Deseas instalar y usar Yarn en lugar de npm? (Y/N)"
REM if errorlevel 2 (
    REM echo Usando npm.
    REM set "PACKAGE_MANAGER=npm"
REM ) else (
    REM echo Seleccionaste Yarn.
    REM call :check_command yarn
    REM if errorlevel 1 (
        REM echo Yarn no encontrado. Intentando instalar Yarn globalmente con npm...
        REM npm install -g yarn
        REM call :check_command yarn
        REM if errorlevel 1 (
            REM echo La instalacion de Yarn fallo. Por favor, instalalo manualmente o elige npm.
            REM echo Continuando con npm por ahora.
            REM set "PACKAGE_MANAGER=npm"
        REM ) else (
            REM echo Yarn instalado correctamente.
            REM set "PACKAGE_MANAGER=yarn"
        REM )
    REM ) else (
        REM set "PACKAGE_MANAGER=yarn"
    REM )
REM )
REM echo Usando %PACKAGE_MANAGER% como gestor de paquetes.

REM Comprobar si existe un package.json
REM if not exist "package.json" (
    REM echo No se encontro el archivo package.json en el directorio actual: %CD%
    REM choice /C YN /M "Deseas crear un nuevo proyecto React llamado '%NEW_PROJECT_NAME%' aqui? (Y/N)"
    REM if errorlevel 2 (
        REM echo Saliendo. Ejecuta el script dentro de un proyecto React existente o permite la creacion de uno nuevo.
        REM goto :eof
    REM ) else (
        REM echo Creando un nuevo proyecto React con 'create-react-app'...
        REM if "%PACKAGE_MANAGER%"=="npm" (
            REM npx create-react-app %NEW_PROJECT_NAME%
        REM ) else (
            REM yarn create react-app %NEW_PROJECT_NAME%
        REM )
        REM if errorlevel 1 (
            REM echo Error creando el proyecto React.
            REM goto :eof
        REM )
        REM cd %NEW_PROJECT_NAME%
        REM if errorlevel 1 (
            REM echo No se pudo cambiar al directorio del nuevo proyecto: %NEW_PROJECT_NAME%
            REM goto :eof
        REM )
        REM echo Nuevo proyecto React '%NEW_PROJECT_NAME%' creado en %CD%.
    REM )
REM )

REM echo Instalando dependencias del proyecto con %PACKAGE_MANAGER%...
REM if "%PACKAGE_MANAGER%"=="npm" (
    REM npm install
REM ) else (
    REM yarn install
REM )

REM if errorlevel 1 (
    REM echo Hubo un error durante la instalacion de dependencias con %PACKAGE_MANAGER%.
    REM goto :eof
REM )
REM echo Dependencias instaladas correctamente.

REM echo Iniciando el servidor de desarrollo de React con %PACKAGE_MANAGER%...
REM if "%PACKAGE_MANAGER%"=="npm" (
    REM echo Ejecutando: npm start
    REM 'start' en batch abre una nueva ventana. Si quieres que se ejecute en la misma, solo 'npm start'.
    REM Sin embargo, 'npm start' es bloqueante.
    REM start "React App Server" npm start
REM ) else (
    REM echo Ejecutando: yarn start
    REM start "React App Server" yarn start
REM )

REM if errorlevel 1 (
    REM echo Hubo un error al iniciar el servidor de desarrollo con %PACKAGE_MANAGER%.
    REM goto :eof
REM )

REM echo El servidor de desarrollo de React deberia estar ejecutandose en una nueva ventana.
REM echo Si no se abrio automaticamente en tu navegador, visita http://localhost:3000 (o el puerto indicado).

echo.
echo Script finalizado (gran parte comentada). Presiona cualquier tecla para salir.
pause >nul

:eof
endlocal
