# 🚀 STRUCT: Generador Automático de Estructuras de Proyectos

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/httpdss/struct/blob/master/README.md) [![es](https://img.shields.io/badge/lang-es-yellow.svg)](https://github.com/httpdss/struct/blob/master/README.es.md)

![Banner de Struct](extras/banner.png)

> [!WARNING]
> Este proyecto aún está en desarrollo y puede contener errores. Úsalo bajo tu propio riesgo.

## 📄 Tabla de Contenidos

- [Introducción](#-introducción)
- [Características](#-características)
- [Instalación](#️-instalación)
  - [Usando pip](#usando-pip)
  - [Desde el código fuente](#desde-el-código-fuente)
  - [Usando Docker](#usando-docker)
- [Inicio Rápido](#-inicio-rápido)
- [Uso](#-uso)
- [Configuración YAML](#-configuración-yaml)
- [Esquema YAML](#-esquema-yaml)
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
- **Variables de Plantilla**: Usa marcadores de posición en tu configuración y reemplázalos con valores reales en tiempo de ejecución. También admite filtros personalizados de Jinja2 y modo interactivo para completar las variables.
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
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:main generate \
  /workdir/example/structure.yaml \
  /workdir/example_output
```

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
struct structure.yaml .
```

## 📝 Uso

Ejecuta el script con el siguiente comando usando uno de los siguientes subcomandos:

- `generate`: Genera la estructura del proyecto basada en la configuración YAML.
- `generate-schema`: Genera esquema JSON para las plantillas de estructura disponibles.
- `validate`: Valida la configuración YAML para asegurarte de que sea válida.
- `info`: Muestra información sobre el script y sus dependencias.
- `list`: Lista las estructuras disponibles.

Para más información, ejecuta el script con la opción `-h` o `--help` (esto también está disponible para cada subcomando):

```sh
struct -h
```

### Ejemplo Simple

```sh
struct generate terraform-module ./mi-modulo-terraform
```

### Ejemplo Más Completo

```sh
struct generate \
  --log=DEBUG \
  --dry-run \
  --vars="project_name=MiProyecto,author_name=JuanPerez" \
  --backup=/ruta/al/respaldo \
  --file-strategy=rename \
  --log-file=/ruta/al/archivo_de_registro.log \
  terraform-module \
  ./mi-modulo-terraform

```

### Comando Generate Schema

El comando `generate-schema` crea definiciones de esquema JSON para las plantillas de estructura disponibles, facilitando que las herramientas e IDEs proporcionen autocompletado y validación.

#### Uso Básico

```sh
# Generar esquema a stdout
struct generate-schema

# Generar esquema con ruta de estructuras personalizada
struct generate-schema -s /ruta/a/estructuras/personalizadas

# Guardar esquema en archivo
struct generate-schema -o schema.json

# Combinar ruta personalizada y archivo de salida
struct generate-schema -s /ruta/a/estructuras/personalizadas -o schema.json
```

#### Opciones del Comando

- `-s, --structures-path`: Ruta a definiciones de estructura adicionales (opcional)
- `-o, --output`: Ruta del archivo de salida para el esquema (predeterminado: stdout)

El esquema generado incluye todas las estructuras disponibles tanto del directorio contribs integrado como de cualquier ruta de estructuras personalizada que especifiques. Esto es útil para:

- Autocompletado IDE al escribir archivos `.struct.yaml`
- Validación de referencias de estructura en tus configuraciones
- Descubrimiento programático de plantillas disponibles

## 📄 Configuración YAML

Aquí tienes un ejemplo de un archivo de configuración YAML:

```yaml
files:
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
      file: https://raw.githubusercontent.com/nishanths/license/master/LICENSE
  - archivo_remoto.txt:
      file: file:///ruta/al/archivo/local.txt
  - archivo_github.py:
      file: github://owner/repo/branch/path/to/file.py
  - archivo_github_https.py:
      file: githubhttps://owner/repo/branch/path/to/file.py
  - archivo_github_ssh.py:
      file: githubssh://owner/repo/branch/path/to/file.py
  - archivo_s3.txt:
      file: s3://bucket_name/key
  - archivo_gcs.txt:
      file: gs://bucket_name/key
  - src/main.py:
      content: |
        print("Hello, World!")
folders:
  - .devops/modules/mod1:
      struct: terraform/module
  - .devops/modules/mod2:
      struct: terraform/module
      with:
        module_name: mymod2
  - ./:
      struct:
        - docker-files
        - project/go
variables:
  - project_name:
      description: "The name of the project"
      default: "MyProject"
      type: string
  - author_name:
      description: "The name of the author"
      type: string
      default: "John Doe"
```

### Variables de plantilla

Puedes usar variables de plantilla en tu archivo de configuración encerrándolas entre `{{@` y `@}}`. Por ejemplo, `{{@ project_name @}}` será reemplazado con el valor de la variable `project_name` en tiempo de ejecución. Si las variables no se proporcionan en la línea de comandos, se solicitarán interactivamente.

Si necesitas definir bloques, puedes usar la notación de inicio de bloque `{%@` y la notación de final de bloque `%@}`.

Para definir comentarios, puedes usar la notación de inicio de comentario `{#@` y la notación de fin de comentario `@#}`.

#### Variables de plantilla predeterminadas

- `file_name`: El nombre del archivo que se está procesando.
- `file_directory`: El nombre del directorio del archivo que se está procesando.

#### Variables de plantilla interactivo

Si no proporcionas todas las variables en la línea de comandos, se solicitarán interactivamente.

La struct definida debe incluir las variables en una seccion de `variables` con la siguiente estructura:

```yaml
variables:
  - variable_name:
      description: "Descripción de la variable"
      type: string
      default: "Valor predeterminado"
```

como puedes ver, cada variable debe tener una descripción, un tipo y un valor predeterminado (opcional). Este valor predeterminado se usará si no se proporciona la variable en la línea de comandos.

#### Filtros personalizados de Jinja2

##### `latest_release`

Este filtro obtiene la versión más reciente de una release en un repositorio de GitHub. Toma el nombre del repositorio como argumento.

```yaml
files:
  - README.md:
      content: |
        # MyProject
        Latest release: {{@ "httpdss/struct" | latest_release @}}
```

Esto utiliza PyGithub para obtener la última release del repositorio, por lo que configurar la variable de entorno `GITHUB_TOKEN` te dará acceso a repositorios privados.

Si ocurre un error en el proceso, el filtro devolverá `LATEST_RELEASE_ERROR`.

NOTA: puedes usar este filtro para obtener la última versión de un proveedor de Terraform. Por ejemplo, para obtener la última versión del proveedor `aws`, puedes usar `{{@ "hashicorp/terraform-provider-aws" | latest_release @}}` o el proveedor de datadog `{{@ "DataDog/terraform-provider-datadog" | latest_release @}}`.

##### `slugify`

Este filtro convierte una cadena en un slug. Toma un argumento opcional para especificar el carácter separador (el valor predeterminado es `-`).

```yaml
files:
  - README.md:
      content: |
        # {{@ project_name @}}
        This is a template repository.
        slugify project_name: {{@ project_name | slugify @}}
```

##### `default_branch`

Este filtro obtiene el nombre de la rama predeterminada de un repositorio de GitHub. Toma el nombre del repositorio como argumento.

```yaml
files:
  - README.md:
      content: |
        # MyProject
        Default branch: {{@ "httpdss/struct" | default_branch @}}
```

### Cláusula `with`

La cláusula `with` te permite pasar variables adicionales a estructuras anidadas. Estas variables se fusionarán con las variables globales y se pueden usar dentro de la estructura anidada.

Ejemplo:

```yaml
folders:
  - .devops/modules/mod1:
      struct: terraform/module
  - .devops/modules/mod2:
      struct: terraform/module
      with:
        module_name: mymod2
```

## 📝 Esquema YAML

Para asegurar que tus archivos de configuración YAML cumplan con la estructura esperada, puedes usar el esquema JSON proporcionado. Esto ayuda a validar tus archivos YAML y proporciona autocompletado en editores compatibles como VSCode.

### Configuración en VSCode

1. Instala la [extensión YAML](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml) para VSCode.
2. Añade la siguiente configuración a los ajustes de tu espacio de trabajo (`.vscode/settings.json`):

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/httpdss/struct/refs/heads/main/struct-schema.json": ".struct.yaml"
  }
}
```

Esta configuración asociará el esquema JSON con todos los archivos .struct.yaml en tu espacio de trabajo, proporcionando validación y autocompletado.

## 🔄 Script de Disparador de GitHub

El script `github-trigger.py` es una utilidad diseñada para activar el flujo de trabajo `run-struct` en todos los repositorios privados de una organización de GitHub que cumplan con ciertos criterios. Este script es especialmente útil para automatizar tareas en múltiples repositorios.

### 📋 Características

- Filtra repositorios por un tema específico (por ejemplo, `struct-enabled`).
- Verifica la existencia de un archivo `.struct.yaml` en la rama predeterminada del repositorio.
- Comprueba la presencia del archivo de flujo de trabajo `run-struct` en `.github/workflows/`.
- Activa el evento de despacho del flujo de trabajo en los repositorios elegibles.

### 🚀 Uso

Para usar el script, asegúrate de cumplir con los siguientes requisitos:

1. Un token de acceso personal de GitHub válido con los permisos necesarios (configurado como la variable de entorno `GITHUB_TOKEN`).
2. La biblioteca `PyGithub` instalada (`pip install PyGithub`).

Ejecuta el script con el siguiente comando:

```sh
python3 scripts/github-trigger.py <organización> <tema>
```

#### Argumentos

- `<organización>`: El nombre de la organización de GitHub.
- `<tema>`: El tema para filtrar los repositorios (por ejemplo, `struct-enabled`).

#### Ejemplo

```sh
export GITHUB_TOKEN=tu_token_de_acceso_personal
python3 scripts/github-trigger.py mi-org struct-enabled
```

### 🛠️ Cómo Funciona

1. El script se conecta a la API de GitHub utilizando el token proporcionado.
2. Itera a través de todos los repositorios privados de la organización especificada.
3. Para cada repositorio:
   - Verifica si el repositorio tiene el tema especificado.
   - Comprueba la existencia de un archivo `.struct.yaml` en la rama predeterminada.
   - Confirma la presencia del archivo de flujo de trabajo `run-struct`.
   - Activa el evento de despacho del flujo de trabajo si se cumplen todas las condiciones.

### ⚠️ Notas

- Asegúrate de configurar la variable de entorno `GITHUB_TOKEN` antes de ejecutar el script.
- El token debe tener permisos suficientes para acceder a repositorios privados y activar flujos de trabajo.
- Los errores durante la ejecución (por ejemplo, archivos faltantes o permisos insuficientes) se registrarán en la consola.

## 🪝 Ganchos de Pre-generación y Post-generación

Puedes definir comandos de shell para ejecutar antes y después de la generación de la estructura usando las claves `pre_hooks` y `post_hooks` en tu configuración YAML. Son opcionales y te permiten automatizar pasos de preparación o limpieza.

- **pre_hooks**: Lista de comandos de shell a ejecutar antes de la generación. Si algún comando falla (código distinto de cero), la generación se aborta.
- **post_hooks**: Lista de comandos de shell a ejecutar después de completar la generación. Si algún comando falla, se muestra un error.

Ejemplo:

```yaml
pre_hooks:
  - echo "Preparando el entorno..."
  - ./scripts/prep.sh

post_hooks:
  - echo "¡Generación completa!"
  - ./scripts/cleanup.sh
files:
  - README.md:
      content: |
        # Mi Proyecto
```

**Notas:**

- La salida de los ganchos (stdout y stderr) se muestra en la terminal.
- Si un pre-hook falla, la generación se detiene.
- Si no se definen hooks, no ocurre nada extra.

## 🗺️ Soporte de Mappings

Puedes proporcionar un archivo YAML de mappings para inyectar mapas clave-valor en tus plantillas. Esto es útil para referenciar valores específicos de entorno, IDs o cualquier otro mapeo que quieras usar en tus archivos generados.

### Ejemplo de archivo de mappings

```yaml
mappings:
  teams:
    devops: devops-team
  aws_account_ids:
    myenv-non-prod: 123456789
    myenv-prod: 987654321
```

### Uso en plantillas

Puedes referenciar valores del mapping en tus plantillas usando la variable `mappings`:

```jinja
{{@ mappings.aws_account_ids['myenv-prod'] @}}
```

Esto se renderizará como:

```text
987654321
```

### Usar mappings en la cláusula `with`

También puedes asignar un valor desde un mapping directamente en la cláusula `with` para llamadas a struct de carpetas. Por ejemplo:

```yaml
folders:
  - ./:
      struct:
        - configs/codeowners
    with:
      team: {{@ mappings.teams.devops @}}
      account_id: {{@ mappings.aws_account_ids['myenv-prod'] @}}
```

Esto asignará el valor `devops-team` a la variable `team` y `987654321` a `account_id` en el struct, usando los valores de tu archivo de mappings.

### Pasar el archivo de mappings

Usa el argumento `--mappings-file` con el comando `generate`:

```sh
struct generate --mappings-file ./mimapa.yaml mi-estructura.yaml .
```

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

- [ ] TBD
