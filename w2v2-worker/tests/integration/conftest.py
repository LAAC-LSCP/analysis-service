from pathlib import Path

from analysis_service_core.testing.mocks import ConfigMock

TESTS = Path(__file__).parents[1]

_FLAT_DATASETS = TESTS / "integration_datasets" / "flat_dataset"
assert _FLAT_DATASETS.exists()

_NESTED_DATASETS = TESTS / "integration_datasets" / "nested_dataset"
assert _NESTED_DATASETS.exists()

_FORWARD_PASSES_FLAT_JSON = TESTS / "forward_passes_flat.json"
assert _FORWARD_PASSES_FLAT_JSON.exists()

_FORWARD_PASSES_NESTED_JSON = (
    TESTS / "forward_passes_nested.json"
)
assert _FORWARD_PASSES_NESTED_JSON.exists()

config_mock = ConfigMock()
