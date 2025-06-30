@echo off
setlocal

REM --- Configuración ---
set "PROJECT_DIR=%CD%"
set "NEW_PROJECT_NAME=mi-app-react"
set "NODE_INSTALLER_URL=https://nodejs.org/dist/v18.18.0/node-v18.18.0-x64.msi"
set "NODE_INSTALLER_NAME=node-installer.msi"

REM --- Funciones Auxiliares (simuladas en Batch) ---

:check_command
    where %1 >nul 2>nul
    if %errorlevel% == 0 (
        echo %1 encontrado.
        exit /b 0
    ) else (
        echo %1 no encontrado.
        exit /b 1
    )

:install_node_npm
    echo Intentando instalar Node.js y npm...
    echo Descargando instalador de Node.js...
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
    exit /b 0

REM --- Flujo Principal ---

REM Comprobar Node.js
call :check_command node
if errorlevel 1 (
    call :install_node_npm
    if errorlevel 1 (
        echo Instalacion de Node.js fallida. Saliendo.
        goto :eof
    )
    echo.
    echo POR FAVOR, CIERRA ESTA VENTANA DE COMANDOS Y ABRE UNA NUEVA.
    echo LUEGO, EJECUTA EL SCRIPT DE NUEVO EN LA NUEVA VENTANA.
    goto :eof
)

REM Comprobar npm
call :check_command npm
if errorlevel 1 (
    echo npm no se encontro a pesar de que Node.js parece estar instalado.
    echo Esto es inusual. Intentando reinstalar Node.js y npm...
    call :install_node_npm
    if errorlevel 1 (
        echo Instalacion de Node.js/npm fallida. Saliendo.
        goto :eof
    )
    echo.
    echo POR FAVOR, CIERRA ESTA VENTANA DE COMANDOS Y ABRE UNA NUEVA.
    echo LUEGO, EJECUTA EL SCRIPT DE NUEVO EN LA NUEVA VENTANA.
    goto :eof
)

set "PACKAGE_MANAGER=npm"
choice /C YN /M "Deseas instalar y usar Yarn en lugar de npm? (Y/N)"
if errorlevel 2 (
    echo Usando npm.
    set "PACKAGE_MANAGER=npm"
) else (
    echo Seleccionaste Yarn.
    call :check_command yarn
    if errorlevel 1 (
        echo Yarn no encontrado. Intentando instalar Yarn globalmente con npm...
        npm install -g yarn
        call :check_command yarn
        if errorlevel 1 (
            echo La instalacion de Yarn fallo. Por favor, instalalo manualmente o elige npm.
            echo Continuando con npm por ahora.
            set "PACKAGE_MANAGER=npm"
        ) else (
            echo Yarn instalado correctamente.
            set "PACKAGE_MANAGER=yarn"
        )
    ) else (
        set "PACKAGE_MANAGER=yarn"
    )
)
echo Usando %PACKAGE_MANAGER% como gestor de paquetes.

REM Comprobar si existe un package.json
if not exist "package.json" (
    echo No se encontro el archivo package.json en el directorio actual: %CD%
    choice /C YN /M "Deseas crear un nuevo proyecto React llamado '%NEW_PROJECT_NAME%' aqui? (Y/N)"
    if errorlevel 2 (
        echo Saliendo. Ejecuta el script dentro de un proyecto React existente o permite la creacion de uno nuevo.
        goto :eof
    ) else (
        echo Creando un nuevo proyecto React con 'create-react-app'...
        if "%PACKAGE_MANAGER%"=="npm" (
            npx create-react-app %NEW_PROJECT_NAME%
        ) else (
            yarn create react-app %NEW_PROJECT_NAME%
        )
        if errorlevel 1 (
            echo Error creando el proyecto React.
            goto :eof
        )
        cd %NEW_PROJECT_NAME%
        if errorlevel 1 (
            echo No se pudo cambiar al directorio del nuevo proyecto: %NEW_PROJECT_NAME%
            goto :eof
        )
        echo Nuevo proyecto React '%NEW_PROJECT_NAME%' creado en %CD%.
    )
)

echo Instalando dependencias del proyecto con %PACKAGE_MANAGER%...
if "%PACKAGE_MANAGER%"=="npm" (
    npm install
) else (
    yarn install
)

if errorlevel 1 (
    echo Hubo un error durante la instalacion de dependencias con %PACKAGE_MANAGER%.
    goto :eof
)
echo Dependencias instaladas correctamente.

echo Iniciando el servidor de desarrollo de React con %PACKAGE_MANAGER%...
if "%PACKAGE_MANAGER%"=="npm" (
    echo Ejecutando: npm start
    REM 'start' en batch abre una nueva ventana. Si quieres que se ejecute en la misma, solo 'npm start'.
    REM Sin embargo, 'npm start' es bloqueante.
    start "React App Server" npm start
) else (
    echo Ejecutando: yarn start
    start "React App Server" yarn start
)

if errorlevel 1 (
    echo Hubo un error al iniciar el servidor de desarrollo con %PACKAGE_MANAGER%.
    goto :eof
)

echo El servidor de desarrollo de React deberia estar ejecutandose en una nueva ventana.
echo Si no se abrio automaticamente en tu navegador, visita http://localhost:3000 (o el puerto indicado).

echo.
echo Script finalizado. Presiona cualquier tecla para salir.
pause >nul

:eof
endlocal
