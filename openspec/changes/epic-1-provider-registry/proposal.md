# Proposal: Epic 1 – Introduce Provider Registry & Config Abstraction

## Scope
Create a provider registry module and abstract cloud configuration out of AWS-specific globals. Provide runtime detection and selection of provider configs without changing end-user behavior for pure AWS use cases.

## Acceptance Criteria
- All existing tests pass without modification.
- New unit tests verify `detect_providers` returns `"aws"` for current AWS fixtures.
- No direct module imports of `AWS_*` constants remain outside `cloud_config` (they should be accessed via a config instance).

## Context from `docs/ARCHITECTUAL.md` (Epic 1 – Introduce Provider Registry & Config Abstraction)
### Implementation Details
- New module: `modules/provider_registry.py` (name is guidance; final name to be aligned with repo conventions).
  - Define:
    ```python
    class ProviderConfig(TypedDict):
        name: str
        resource_prefixes: List[str]
        config: CloudConfig  # see below
        graph_transformers: List[Callable[[dict, CloudConfig], dict]]
        drawing: DrawingConfig
    ```
    - For now, create `AwsProviderConfig` only, wired from existing `cloud_config.AWS_*`.
  - Implement:
    - `detect_providers(tfdata) -> List[ProviderConfig]` using prefixes found in `tfdata["graphdict"]` and `tfdata["meta_data"]`.
    - `get_primary_provider(providers) -> ProviderConfig`:
      - Choose provider with largest number of resources; fallback to AWS for backward compatibility when ambiguous.
- Refactor `modules/cloud_config.py`:
  - Wrap AWS constants into a `CloudConfig` data structure (e.g., dataclass or dict) rather than top-level `AWS_*` constants.
  - Keep AWS names but access them through an `AwsCloudConfig` instance.
  - Do not introduce Azure/GCP constants yet; stub empty configs:
    ```python
    AZURE_CONFIG = CloudConfig(...)
    GCP_CONFIG = CloudConfig(...)
    ```
    with minimal defaults.
- Update `tfwrapper.tf_makegraph`, `graphmaker`, `resource_handlers`, and `drawing` signatures to accept a `provider_config` (even if they initially only ever receive AWS):
  - For now, get provider inside CLI:
    - After `compile_tfdata`, compute `provider = detect_providers(tfdata)[0]` and pass to downstream calls.
