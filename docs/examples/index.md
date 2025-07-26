# Examples

This directory contains practical examples of STRUCT configurations for various use cases.

## Basic Examples

- [Simple Project](simple-project.yaml) - Basic project structure with files and folders
- [Template Variables](template-variables.yaml) - Using dynamic content with variables
- [Remote Files](remote-files.yaml) - Fetching content from external sources

## Application Development

- [Python Project](python-project.yaml) - Complete Python application structure
- [Node.js API](nodejs-api.yaml) - REST API with Express.js
- [React Frontend](react-frontend.yaml) - Modern React application setup
- [Microservice](microservice.yaml) - Containerized microservice template

## Infrastructure

- [Terraform Module](terraform-module.yaml) - AWS infrastructure module
- [Kubernetes Application](k8s-application.yaml) - Complete K8s deployment
- [Docker Multi-Stage](docker-multistage.yaml) - Multi-stage Docker setup
- [CI/CD Pipeline](cicd-pipeline.yaml) - GitHub Actions workflow

## DevOps

- [Monitoring Setup](monitoring.yaml) - Prometheus and Grafana configuration
- [GitOps Repository](gitops-repo.yaml) - ArgoCD application structure
- [Helm Chart](helm-chart.yaml) - Kubernetes Helm chart template

## Advanced

- [Multi-Environment](multi-environment.yaml) - Environment-specific configurations with mappings
- [Custom Hooks](custom-hooks.yaml) - Complex automation with pre/post hooks
- [Modular Structure](modular-structure.yaml) - Composable, reusable components

## Usage

Each example can be used directly:

```bash
# Use an example from this directory
struct generate ./docs/examples/python-project.yaml ./my-project

# Or reference the raw URL
struct generate https://raw.githubusercontent.com/httpdss/struct/main/docs/examples/python-project.yaml ./my-project
```

## Contributing Examples

We welcome community examples! To contribute:

1. Create a new `.yaml` file in this directory
2. Follow the naming convention: `descriptive-name.yaml`
3. Include comments explaining key concepts
4. Add the example to this index
5. Submit a pull request

### Example Template

```yaml
# Example: [Brief Description]
# Use case: [What this example demonstrates]
# Requirements: [Any prerequisites or dependencies]

files:
  - README.md:
      content: |
        # Example Project
        This demonstrates [key concept]

variables:
  - example_var:
      description: "Example variable"
      type: string
      default: "example_value"
```
