from pathlib import Path
from uuid import UUID

from analysis_service_core.testing.mocks import ConfigMock

_TASK_ID = UUID("00000000-0000-0000-0000-000000000001")

_FLAT_DATASETS = Path(__file__).parent.parent / "flat_datasets"
assert _FLAT_DATASETS.exists()

_NESTED_DATASETS = Path(__file__).parent.parent / "nested_datasets"
assert _NESTED_DATASETS.exists()

_FORWARD_PASSES_FLAT_JSON = Path(__file__).parent.parent / "forward_passes_flat.json"
_FORWARD_PASSES_NESTED_JSON = Path(__file__).parent.parent / "forward_passes_nested.json"

flat_config_mock = ConfigMock(
    overrides={
        "ALICE_FOLDER": _FLAT_DATASETS / "stage_0" / "outputs" / "00000000-0000-0000-0000-000000000001" / "alice_folder",
    }
)

nested_config_mock = ConfigMock(
    overrides={
        "ALICE_FOLDER": _NESTED_DATASETS / "stage_0" / "outputs" / "00000000-0000-0000-0000-000000000001" / "alice_folder",
    }
)
