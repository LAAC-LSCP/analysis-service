from pathlib import Path

from analysis_service_core.testing.mocks import ConfigMock

TESTS = Path(__file__).parents[1]

_FLAT_DATASET = TESTS / "integration_datasets" / "flat_dataset"
assert _FLAT_DATASET.exists()

_NESTED_DATASET = TESTS / "integration_datasets" / "nested_dataset"
assert _NESTED_DATASET.exists()

_FORWARD_PASSES_FLAT_JSON = TESTS / "forward_passes_flat.json"
assert _FORWARD_PASSES_FLAT_JSON.exists()

_FORWARD_PASSES_NESTED_JSON = TESTS / "forward_passes_nested.json"
assert _FORWARD_PASSES_NESTED_JSON.exists()

flat_config_mock = ConfigMock(
    overrides={
        "ALICE_FOLDER": _FLAT_DATASET
        / "stage_0"
        / "outputs"
        / "00000000-0000-0000-0000-000000000001"
        / "alice_folder",
    }
)

nested_config_mock = ConfigMock(
    overrides={
        "ALICE_FOLDER": _NESTED_DATASET
        / "stage_0"
        / "outputs"
        / "00000000-0000-0000-0000-000000000001"
        / "alice_folder",
    }
)
