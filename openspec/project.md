# Project Context

## Purpose
TerraVision is a Python-based CLI tool that automatically generates professional cloud architecture diagrams from Terraform code. It solves the problem of stale documentation by enabling "Docs as Code" (DaC). It runs 100% client-side, securely, without requiring access to the cloud environment, by parsing Terraform plans and code to visualize resources and their relationships.

## Tech Stack
- **Language:** Python (3.10+)
- **CLI Framework:** Click
- **Infrastructure as Code:** Terraform (v1.0+)
- **Visualization Engine:** Graphviz (DOT language)
- **Parsing:** python-hcl2
- **Dependency Management:** Poetry
- **VCS:** Git

## Project Conventions

### Code Style
- **Formatter:** `black` (line-length 88)
- **Import Sorting:** `isort`
- **Linting:** `ruff` / `flake8` (planned)
- **Type Hinting:** Optional but encouraged for new code (mypy planned).
- **Naming:** Standard Python snake_case for functions and variables, PascalCase for classes.

### Architecture Patterns
- **Pipeline:** Linear processing pipeline: `CLI` -> `TFWrapper` (Plan) -> `FileParser` (HCL) -> `Interpreter` (Context) -> `GraphMaker` (Logic) -> `Drawing` (Render).
- **Provider Abstraction:** (In Progress) Moving from hardcoded AWS logic to a plugin-based `ProviderConfig` system to support Azure, GCP, and others.
- **Client-Side:** All logic executes locally; no calls to cloud provider APIs.

### Testing Strategy
- **Framework:** `pytest`
- **Unit Tests:** Located in `tests/*_unit_test.py`. rapid execution, mocking external binaries where possible.
- **Integration Tests:** End-to-end tests generating diagrams from fixtures in `tests/json`.
- **Golden Tests:** Comparison against known-good reference diagrams (planned).

### Git Workflow
- **Branching:** Feature branches merged into `main` via Pull Request.
- **Commits:** Clear, concise messages.
- **Pre-commit:** Hooks for linting and formatting are available.

## Domain Context
- **Terraform Semantics:** Deep understanding of HCL2, Resources, Data Sources, Modules, Variables, Locals, and `terraform plan` JSON output structure.
- **Cloud Topology:** Knowledge of cloud provider resource hierarchies (e.g., AWS: Region -> VPC -> Availability Zone -> Subnet -> Instance).
- **Graph Visualization:** Mapping infrastructure topology to directed graphs (Nodes, Edges, Clusters/Subgraphs).

## Important Constraints
- **No Cloud Access:** The tool must function without AWS/Azure/GCP credentials. It relies solely on the Terraform code and plan data.
- **Binary Dependencies:** Requires `terraform` and `graphviz` executables to be present in the system PATH.
- **OS Support:** Primary support for macOS and Linux; Windows support via WSL or PowerShell.

## External Dependencies
- **System Binaries:**
    - `terraform` (>= 1.0)
    - `dot` (Graphviz)
    - `git`
- **Python Libraries:**
    - `click`
    - `graphviz`
    - `python-hcl2`
    - `pyyaml`
