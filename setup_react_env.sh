#!/bin/bash

# Función para instalar Node.js y npm si no están presentes
install_node_npm() {
    echo "Node.js y npm no encontrados. Intentando instalarlos..."
    # Detectar el gestor de paquetes del sistema
    if command -v apt-get &> /dev/null; then
        echo "Usando apt-get para la instalación..."
        sudo apt-get update
        sudo apt-get install -y nodejs npm
    elif command -v yum &> /dev/null; then
        echo "Usando yum para la instalación..."
        sudo yum install -y nodejs npm
    elif command -v brew &> /dev/null; then
        echo "Usando Homebrew para la instalación..."
        brew install node
    else
        echo "No se pudo detectar un gestor de paquetes compatible (apt-get, yum, brew)."
        echo "Por favor, instala Node.js y npm manualmente."
        exit 1
    fi
    # Verificar la instalación
    if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
        echo "La instalación de Node.js y npm falló."
        echo "Por favor, instálalos manualmente."
        exit 1
    fi
    echo "Node.js y npm instalados correctamente."
}

# Comprobar si Node.js está instalado
if ! command -v node &> /dev/null; then
    install_node_npm
else
    echo "Node.js ya está instalado."
fi

# Comprobar si npm está instalado (generalmente viene con Node.js, pero es bueno verificar)
if ! command -v npm &> /dev/null; then
    echo "npm no encontrado, intentando instalar..."
    install_node_npm # Reutilizamos la función, aunque si node está, npm debería estar.
else
    echo "npm ya está instalado."
fi

# Preguntar al usuario si prefiere Yarn (opcional)
read -p "¿Deseas instalar y usar Yarn en lugar de npm? (s/N): " use_yarn
use_yarn_lower=$(echo "$use_yarn" | tr '[:upper:]' '[:lower:]')

package_manager="npm"

if [[ "$use_yarn_lower" == "s" ]]; then
    if ! command -v yarn &> /dev/null; then
        echo "Yarn no encontrado. Intentando instalar Yarn..."
        # Instalar Yarn usando npm
        sudo npm install -g yarn
        if ! command -v yarn &> /dev/null; then
            echo "La instalación de Yarn falló. Por favor, instálalo manualmente."
            # Se podría continuar con npm o salir, por ahora continuaremos con npm si yarn falla.
            echo "Continuando con npm."
        else
            echo "Yarn instalado correctamente."
            package_manager="yarn"
        fi
    else
        echo "Yarn ya está instalado."
        package_manager="yarn"
    fi
fi

echo "Usando $package_manager como gestor de paquetes."

# Comprobar si existe un package.json en el directorio actual
if [ ! -f package.json ]; then
    echo "No se encontró el archivo package.json en el directorio actual."
    echo "Asegúrate de estar en el directorio raíz de tu proyecto React."
    # Preguntar si se desea crear un nuevo proyecto React
    read -p "¿Deseas crear un nuevo proyecto React llamado 'mi-app-react' en este directorio? (s/N): " create_new_project
    create_new_project_lower=$(echo "$create_new_project" | tr '[:upper:]' '[:lower:]')
    if [[ "$create_new_project_lower" == "s" ]]; then
        echo "Creando un nuevo proyecto React con 'create-react-app'..."
        if [[ "$package_manager" == "npm" ]]; then
            npx create-react-app mi-app-react
        else # yarn
            yarn create react-app mi-app-react
        fi
        cd mi-app-react || { echo "No se pudo cambiar al directorio del nuevo proyecto."; exit 1; }
        echo "Nuevo proyecto React 'mi-app-react' creado."
    else
        echo "Saliendo. Ejecuta el script dentro de un proyecto React existente o permite la creación de uno nuevo."
        exit 1
    fi
fi

echo "Instalando dependencias del proyecto con $package_manager..."
if [[ "$package_manager" == "npm" ]]; then
    npm install
else # yarn
    yarn install
fi

if [ $? -ne 0 ]; then
    echo "Hubo un error durante la instalación de dependencias con $package_manager."
    exit 1
fi
echo "Dependencias instaladas correctamente."

echo "Iniciando el servidor de desarrollo de React con $package_manager..."
if [[ "$package_manager" == "npm" ]]; then
    npm start
else # yarn
    yarn start
fi

if [ $? -ne 0 ]; then
    echo "Hubo un error al iniciar el servidor de desarrollo con $package_manager."
    exit 1
fi

echo "El servidor de desarrollo de React debería estar ejecutándose."
echo "Si no se abrió automáticamente en tu navegador, visita http://localhost:3000 (o el puerto indicado)."
