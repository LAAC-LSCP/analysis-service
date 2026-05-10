from pathlib import Path

from analysis_service_core.testing.mocks import ConfigMock

TESTS = Path(__file__).parents[1]

_FORWARD_PASSES_FLAT_JSON = TESTS / "forward_passes_flat.json"
assert _FORWARD_PASSES_FLAT_JSON.exists()

_FORWARD_PASSES_NESTED_JSON = TESTS / "forward_passes_nested.json"
assert _FORWARD_PASSES_NESTED_JSON.exists()

_FLAT_DATASET = TESTS / "integration_datasets" / "flat_dataset"
assert _FLAT_DATASET.exists()

_NESTED_DATASET = TESTS / "integration_datasets" / "nested_dataset"
assert _NESTED_DATASET.exists()

config = ConfigMock(
    overrides={
        "VTC_FOLDER": Path("/temp"),
        "VTC_DEVICE": "cpu",
        "CONDA_ACTIVATE_FILE": "",
        "CONDA_ENV_NAME": "",
    }
)
