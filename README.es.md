
# 🚀 STRUCT: Generador Automático de Estructuras de Proyectos

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/httpdss/struct/blob/master/README.md) [![es](https://img.shields.io/badge/lang-es-yellow.svg)](https://github.com/httpdss/struct/blob/master/README.es.md)

![Banner de Struct](extras/banner.png)

> [!WARNING]
> Este proyecto aún está en desarrollo y puede contener errores. Úsalo bajo tu propio riesgo.

## 📄 Tabla de Contenidos

- [Introducción](#-introducción)
- [Características](#-características)
- [Instalación](#instalación)
  - [Usando pip](#usando-pip)
  - [Desde el código fuente](#desde-el-código-fuente)
  - [Usando Docker](#usando-docker)
- [Inicio Rápido](#-inicio-rápido)
- [Uso](#-uso)
- [Configuración YAML](#-configuración-yaml)
- [Desarrollo](#-desarrollo)
- [Licencia](#-licencia)
- [Financiamiento](#-financiamiento)
- [Contribuyendo](#-contribuyendo)
- [Agradecimientos](#-agradecimientos)
- [Problemas Conocidos](#-problemas-conocidos)

## 📦 Introducción

STRUCT es un script potente y flexible diseñado para automatizar la creación de estructuras de proyectos basadas en configuraciones YAML. Admite variables de plantilla, permisos de archivos personalizados, obtención de contenido remoto y múltiples estrategias de manejo de archivos para optimizar tu proceso de configuración de desarrollo.

Está dirigido a desarrolladores, ingenieros DevOps y cualquier persona que quiera automatizar la creación de estructuras de proyectos. Puede usarse para generar código de plantilla, archivos de configuración, documentación y más.

## ✨ Características

- **Configuración YAML**: Define la estructura de tu proyecto en un simple archivo YAML.
- **Variables de Plantilla**: Usa marcadores de posición en tu configuración y reemplázalos con valores reales en tiempo de ejecución.
- **Permisos de Archivos Personalizados**: Establece permisos personalizados para tus archivos directamente desde la configuración YAML.
- **Obtención de Contenido Remoto**: Incluye contenido de archivos remotos especificando sus URLs.
- **Estrategias de Manejo de Archivos**: Elige entre múltiples estrategias (sobrescribir, omitir, añadir, renombrar, respaldar) para gestionar archivos existentes.
- **Ejecutar en Seco**: Previsualiza las acciones sin hacer cambios en tu sistema de archivos.
- **Validación de Configuración**: Asegura que tu configuración YAML es válida antes de ejecutar el script.
- **Registro Detallado**: Obtén registros detallados de las acciones del script para una fácil depuración y monitoreo.

## 🛠️ Instalación

### Usando pip

Puedes instalar STRUCT usando pip:

```sh
pip install git+https://github.com/httpdss/struct.git
```

### Desde el código fuente

Alternativamente, puedes clonar el repositorio e instalarlo localmente. Consulta la sección [Desarrollo](#-desarrollo) para más detalles.

### Usando Docker

Puedes usar la imagen de Docker para ejecutar el script sin instalarlo en tu sistema. Consulta la sección [Inicio Rápido](#-inicio-rápido) para más detalles.

## 🐳 Inicio Rápido

### Inicio Rápido Usando Docker

1. Crea un archivo de configuración YAML para la estructura de tu proyecto. Consulta una configuración de ejemplo [aquí](./example/structure.yaml).
2. Ejecuta el siguiente comando para generar la estructura del proyecto:

```sh
docker run \
  -v $(pwd):/workdir \
  -e OPENAI_API_KEY=tu-clave \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:main \
  /workdir/example/structure.yaml \
  /workdir/example_output
```

Reemplaza `tu-clave` con tu clave de API de OpenAI y ajusta las rutas según sea necesario. Si no estás usando prompts dentro de tu estructura, puedes establecer `OPENAI_API_KEY` en cualquier valor. Existe un problema conocido con el script que requiere que `OPENAI_API_KEY` esté configurado. Consulta [Problemas Conocidos](#-problemas-conocidos) para más detalles.

### Inicio Rápido Usando Docker Alpine

Para pruebas, puedes ejecutar un contenedor Docker de Alpine e instalar el script dentro de él:

```sh
docker run -it --entrypoint="" python:3.10-alpine sh -l
```

Dentro del contenedor:

```sh
apk add python-pip git vim
pip install git+https://github.com/httpdss/struct.git
mkdir example
cd example/
touch structure.yaml
vim structure.yaml # copia el contenido de la carpeta de ejemplo
export OPENAI_API_KEY=algo
struct structure.yaml .
```

## 📝 Uso

Ejecuta el script con el siguiente comando:

```sh
usage: struct [-h] [--log LOG] [--dry-run] [--vars VARS] [--backup BACKUP] [--file-strategy {overwrite,skip,append,rename,backup}] [--log-file LOG_FILE] yaml_file base_path
```

### Opciones

- `-h` o `--help`: Muestra la ayuda y sale.
- `--log`: Establece el nivel de registro (DEBUG, INFO, WARNING, ERROR, CRITICAL). El valor predeterminado es INFO.
- `--dry-run`: Realiza una ejecución en seco sin crear archivos o directorios.
- `--vars`: Variables de plantilla en el formato `CLAVE1=valor1,CLAVE2=valor2`.
- `--backup`: Ruta a la carpeta de respaldo.
- `--file-strategy`: Estrategia para manejar archivos existentes (sobrescribir, omitir, añadir, renombrar, respaldar). El valor predeterminado es sobrescribir.
- `--log-file`: Ruta a un archivo de registro.

### Ejemplo

```sh
struct \
  --log=DEBUG \
  --dry-run \
  --vars="project_name=MiProyecto,author_name=JuanPerez" \
  --backup=/ruta/al/respaldo \
  --file-strategy=rename \
  --log-file=/ruta/al/archivo_de_registro.log \
  ./example/structure.yaml \
  /ruta/a/tu/directorio/de/salida
```

## 📄 Configuración YAML

Aquí tienes un ejemplo de un archivo de configuración YAML:

```yaml
structure:
  - README.md:
      content: |
        # {{@ project_name @}}
        This is a template repository.
  - script.sh:
      permissions: '0777'
      content: |
        #!/bin/bash
        echo "Hello, {{@ author_name @}}!"
  - LICENSE:
      remote_file: https://raw.githubusercontent.com/nishanths/license/master/LICENSE
  - src/main.py:
      content: |
        print("Hello, World!")
```

### Variables de plantilla

Puedes usar variables de plantilla en tu archivo de configuración encerrándolas entre `{{@` y `@}}`. Por ejemplo, `{{@ project_name @}}` será reemplazado con el valor de la variable `project_name` en tiempo de ejecución.

Si necesitas definir bloques, puedes usar la notación de inicio de bloque `{%@` y la notación de final de bloque `%@}`.

Para definir comentarios, puedes usar la notación de inicio de comentario `{#@` y la notación de fin de comentario `@#}`.

#### Variables de plantilla predeterminadas

- `file_name`: El nombre del archivo que se está procesando.
- `file_directory`: El nombre del directorio del archivo que se está procesando.

#### Filtros personalizados de Jinja2

##### `latest_release`

Este filtro obtiene la versión más reciente de una release en un repositorio de GitHub. Toma el nombre del repositorio como argumento.

```yaml
structure:
  - README.md:
      content: |
        # MyProject
        Latest release: {{@ "httpdss/struct" | latest_release @}}
```

Esto utiliza PyGithub para obtener la última release del repositorio, por lo que configurar la variable de entorno `GITHUB_TOKEN` te dará acceso a repositorios privados.

Si ocurre un error en el proceso, el filtro devolverá `LATEST_RELEASE_ERROR`.

## 👩‍💻 Desarrollo

Para comenzar con el desarrollo, sigue estos pasos:

- Clona el repositorio
- Crea un entorno virtual

```sh
python3 -m venv .venv
source .venv/bin/activate
```

- Instala las dependencias

```sh
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## 💰 Financiamiento

Si encuentras este proyecto útil, considera apoyarlo a través de donaciones: [patreon/structproject](https://patreon.com/structproject)

## 🤝 Contribuyendo

¡Las contribuciones son bienvenidas! Por favor, abre un issue o envía un pull request.

## 🙏 Agradecimientos

Un agradecimiento especial a todos los contribuyentes que hicieron posible este proyecto.

## 🐞 Problemas Conocidos

- [ ] Es obligatorio configurar la variable de entorno `OPENAI_API_KEY` antes de ejecutar el script. Si no estás usando propiedades GPT, puedes establecerla en cualquier valor. Problema [#3](https://github.com/httpdss/struct/issues/3)
