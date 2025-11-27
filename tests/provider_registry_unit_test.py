import unittest, sys, os

parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir)

from modules.provider_registry import (
    ProviderConfig,
    detect_providers,
    get_primary_provider,
    AWS_PROVIDER_CONFIG,
    AZURE_PROVIDER_CONFIG,
    GCP_PROVIDER_CONFIG,
)


class TestProviderRegistry(unittest.TestCase):
    def test_detect_providers_aws_only(self):
        tfdata = {
            "all_resource": {"aws_instance.web": {}, "aws_vpc.main": {}},
            "tf_resources_created": {"aws_instance.web": {}, "aws_vpc.main": {}},
        }
        detected = detect_providers(tfdata)
        self.assertEqual(len(detected), 1)
        self.assertEqual(detected[0]["name"], "aws")

    def test_detect_providers_azure_only(self):
        tfdata = {
            "all_resource": {"azurerm_resource_group.rg": {}},
            "tf_resources_created": {"azurerm_resource_group.rg": {}},
        }
        detected = detect_providers(tfdata)
        self.assertEqual(len(detected), 1)
        self.assertEqual(detected[0]["name"], "azure")

    def test_detect_providers_gcp_only(self):
        tfdata = {
            "all_resource": {"google_compute_instance.vm": {}},
            "tf_resources_created": {"google_compute_instance.vm": {}},
        }
        detected = detect_providers(tfdata)
        self.assertEqual(len(detected), 1)
        self.assertEqual(detected[0]["name"], "gcp")

    def test_detect_providers_multi_cloud(self):
        tfdata = {
            "all_resource": {
                "aws_instance.web": {},
                "azurerm_resource_group.rg": {},
                "google_compute_instance.vm": {},
            },
            "tf_resources_created": {
                "aws_instance.web": {},
                "azurerm_resource_group.rg": {},
                "google_compute_instance.vm": {},
            },
        }
        detected = detect_providers(tfdata)
        self.assertEqual(len(detected), 3)
        detected_names = sorted([p["name"] for p in detected])
        self.assertEqual(detected_names, ["aws", "azure", "gcp"])

    def test_detect_providers_no_providers(self):
        tfdata = {
            "all_resource": {"local_file.test": {}},
            "tf_resources_created": {"local_file.test": {}},
        }
        detected = detect_providers(tfdata)
        self.assertEqual(len(detected), 0)

    def test_get_primary_provider_single(self):
        tfdata = {
            "all_resource": {"aws_instance.web": {}, "aws_vpc.main": {}},
            "tf_resources_created": {"aws_instance.web": {}, "aws_vpc.main": {}},
        }
        providers = [AWS_PROVIDER_CONFIG]
        primary = get_primary_provider(providers, tfdata)
        self.assertEqual(primary["name"], "aws")

    def test_get_primary_provider_majority(self):
        tfdata = {
            "all_resource": {
                "aws_instance.web": {},
                "aws_vpc.main": {},
                "aws_s3_bucket.data": {},
                "azurerm_resource_group.rg": {},
            },
            "tf_resources_created": {
                "aws_instance.web": {},
                "aws_vpc.main": {},
                "aws_s3_bucket.data": {},
                "azurerm_resource_group.rg": {},
            },
        }
        providers = [AWS_PROVIDER_CONFIG, AZURE_PROVIDER_CONFIG]
        primary = get_primary_provider(providers, tfdata)
        self.assertEqual(primary["name"], "aws")

    def test_get_primary_provider_tie_aws_preference(self):
        tfdata = {
            "all_resource": {
                "aws_instance.web": {},
                "azurerm_resource_group.rg": {},
            },
            "tf_resources_created": {
                "aws_instance.web": {},
                "azurerm_resource_group.rg": {},
            },
        }
        providers = [AWS_PROVIDER_CONFIG, AZURE_PROVIDER_CONFIG]
        primary = get_primary_provider(providers, tfdata)
        self.assertEqual(primary["name"], "aws")

    def test_get_primary_provider_empty_list(self):
        tfdata = {
            "all_resource": {},
            "tf_resources_created": {},
        }
        providers = []
        primary = get_primary_provider(providers, tfdata)
        self.assertEqual(primary["name"], "aws")  # Should fallback to AWS

    def test_get_primary_provider_only_tfplan_resources(self):
        tfdata = {
            "all_resource": {},
            "tf_resources_created": {
                "aws_instance.web": {},
                "aws_vpc.main": {},
            },
        }
        providers = [AWS_PROVIDER_CONFIG]
        primary = get_primary_provider(providers, tfdata)
        self.assertEqual(primary["name"], "aws")
    
    def test_get_primary_provider_only_all_resource(self):
        tfdata = {
            "all_resource": {
                "azurerm_resource_group.rg": {},
                "azurerm_virtual_network.vnet": {},
            },
            "tf_resources_created": {},
        }
        providers = [AZURE_PROVIDER_CONFIG]
        primary = get_primary_provider(providers, tfdata)
        self.assertEqual(primary["name"], "azure")

if __name__ == "__main__":
    unittest.main(exit=False)