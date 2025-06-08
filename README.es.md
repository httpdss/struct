# 🚀 STRUCT: Generador Automático de Estructuras de Proyectos

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/httpdss/struct/blob/master/README.md)
[![es](https://img.shields.io/badge/lang-es-yellow.svg)](https://github.com/httpdss/struct/blob/master/README.es.md)

![Banner de Struct](extras/banner.png)

STRUCT automatiza la creación de estructuras de proyectos con plantillas YAML. Está pensado para desarrolladores y equipos DevOps que necesitan andamiajes reproducibles.

## Características 🎯

- Definición de estructuras con YAML
- Variables de plantilla con soporte interactivo
- Permisos de archivos personalizados
- Inclusión de archivos remotos
- Estrategias para archivos existentes
- Modo de prueba y validación
- Registro detallado

## Inicio rápido ⚡

Instalación con pip:

```sh
pip install git+https://github.com/httpdss/struct.git
```

O mediante la imagen Docker:

```sh
docker run \
  -v $(pwd):/workdir \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/struct:main generate \
  /workdir/example/structure.yaml \
  /workdir/example_output
```

## Documentación 📚

Encuentra la documentación completa en [`docs/es`](docs/es) o consulta la versión en inglés en [`docs/en`](docs/en).

- [Instalación](docs/es/installation.md)
- [Uso](docs/es/usage.md)
- [Referencia de configuración YAML](docs/es/configuration.md)
- [Esquema YAML](docs/es/yaml_schema.md)
- [Script de GitHub](docs/es/github_trigger_script.md)
- [Desarrollo](docs/es/development.md)
- [Autocompletado](docs/es/completion.md)
- [Hooks](docs/es/hooks.md)
- [Artículos](docs/es/articles.md)
- [Estructuras disponibles](docs/es/structures.md)

## Licencia

Este proyecto está bajo la Licencia MIT. Revisa el archivo [LICENSE](LICENSE) para más información.

## Financiamiento

Si este proyecto te resulta útil, considera apoyarlo mediante donaciones: [patreon/structproject](https://patreon.com/structproject)

## Contribuyendo

¡Las contribuciones son bienvenidas! Abre un issue o envía un pull request.

## Agradecimientos

Gracias a todas las personas que han contribuido a este proyecto.

## Problemas conocidos

- [ ] TBD
