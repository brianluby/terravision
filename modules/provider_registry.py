from typing import Callable, List, TypedDict, Any, Dict
from modules.cloud_config import CloudConfig, AWS_CLOUD_CONFIG, AZURE_CLOUD_CONFIG, GCP_CLOUD_CONFIG

# Placeholder for DrawingConfig - will be detailed later if needed, for now just a pass
class DrawingConfig(TypedDict):
    # This will contain drawing specific configurations like DRAW_ORDER, etc.
    pass

class ProviderConfig(TypedDict):
    name: str
    resource_prefixes: List[str]
    config: CloudConfig
    graph_transformers: List[Callable[[dict, CloudConfig], dict]]
    drawing: DrawingConfig

# Define concrete ProviderConfig instances
AWS_PROVIDER_CONFIG: ProviderConfig = {
    "name": "aws",
    "resource_prefixes": ["aws_", "data.aws_"],
    "config": AWS_CLOUD_CONFIG,
    "graph_transformers": [], # To be populated in subsequent epics
    "drawing": {}, # To be populated in subsequent epics
}

AZURE_PROVIDER_CONFIG: ProviderConfig = {
    "name": "azure",
    "resource_prefixes": ["azurerm_"],
    "config": AZURE_CLOUD_CONFIG,
    "graph_transformers": [],
    "drawing": {},
}

GCP_PROVIDER_CONFIG: ProviderConfig = {
    "name": "gcp",
    "resource_prefixes": ["google_", "google_beta_"],
    "config": GCP_CLOUD_CONFIG,
    "graph_transformers": [],
    "drawing": {},
}

ALL_PROVIDER_CONFIGS = [AWS_PROVIDER_CONFIG, AZURE_PROVIDER_CONFIG, GCP_PROVIDER_CONFIG]

def detect_providers(tfdata: Dict[str, Any]) -> List[ProviderConfig]:
    """
    Detects which cloud providers are present in the Terraform data.

    Args:
        tfdata: The compiled Terraform data, including resource information.

    Returns:
        A list of ProviderConfig objects for detected providers.
    """
    detected_providers = set()
    all_resources = tfdata.get("all_resource", {})
    tfplan_resources_list = tfdata.get("tf_resources_created", []) # Renamed to avoid confusion and default to list

    for provider_cfg in ALL_PROVIDER_CONFIGS:
        for prefix in provider_cfg["resource_prefixes"]:
            # Check in all_resource (from HCL parsing)
            for resource_name in all_resources.keys():
                if resource_name.startswith(prefix):
                    detected_providers.add(provider_cfg["name"])
                    break
            if provider_cfg["name"] in detected_providers:
                break
            
            # Check in tf_resources_created (from terraform plan output)
            for resource_change_obj in tfplan_resources_list: # Iterate through the list
                if isinstance(resource_change_obj, dict) and "address" in resource_change_obj:
                    if resource_change_obj["address"].startswith(prefix):
                        detected_providers.add(provider_cfg["name"])
                        break
            if provider_cfg["name"] in detected_providers:
                break


    return [cfg for cfg in ALL_PROVIDER_CONFIGS if cfg["name"] in detected_providers]

def get_primary_provider(providers: List[ProviderConfig], tfdata: Dict[str, Any]) -> ProviderConfig:
    """
    Determines the primary provider from a list of detected providers.

    Args:
        providers: A list of detected ProviderConfig objects.
        tfdata: The compiled Terraform data.

    Returns:
        The primary ProviderConfig. Defaults to AWS if no other provider is more dominant or
        if providers list is empty.
    """
    if not providers:
        return AWS_PROVIDER_CONFIG # Default to AWS if no providers detected

    provider_resource_counts: Dict[str, int] = {cfg["name"]: 0 for cfg in providers}
    all_resources = tfdata.get("all_resource", {})
    tfplan_resources_list = tfdata.get("tf_resources_created", [])

    for provider_cfg in providers:
        for prefix in provider_cfg["resource_prefixes"]:
            for resource_name in all_resources.keys():
                if resource_name.startswith(prefix):
                    provider_resource_counts[provider_cfg["name"]] += 1
            for resource_change_obj in tfplan_resources_list:
                if isinstance(resource_change_obj, dict) and "address" in resource_change_obj:
                    if resource_change_obj["address"].startswith(prefix):
                        provider_resource_counts[provider_cfg["name"]] += 1
    
    # Sort providers by resource count in descending order, with AWS prioritized on ties
    sorted_providers = sorted(
        providers,
        key=lambda cfg: (
            provider_resource_counts.get(cfg["name"], 0),
            1 if cfg["name"] == "aws" else 0  # Prioritize AWS in case of a tie
        ),
        reverse=True
    )
    
    return sorted_providers[0] if sorted_providers else AWS_PROVIDER_CONFIG
