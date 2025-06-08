# 🚀 STRUCT: Generador Automático de Estructuras de Proyectos

[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/httpdss/struct/blob/master/README.md) [![es](https://img.shields.io/badge/lang-es-yellow.svg)](https://github.com/httpdss/struct/blob/master/README.es.md)

![Banner de Struct](extras/banner.png)

STRUCT automatiza la creación de estructuras de proyectos a partir de plantillas YAML. Está orientado a desarrolladores y equipos DevOps que buscan un andamiaje reproducible de forma sencilla.

## Características

- Definición de estructuras con YAML
- Variables de plantilla con soporte interactivo
- Permisos de archivos personalizados
- Inclusión de archivos remotos
- Estrategias para gestionar archivos existentes
- Modo de prueba y validación
- Registro detallado

## Inicio rápido

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

## Documentación

La documentación completa se encuentra en la carpeta [docs](docs). Consulta allí las guías de instalación, uso y configuración detallada.

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
