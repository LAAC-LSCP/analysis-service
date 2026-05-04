from pathlib import Path

_FORWARD_PASSES_FLAT_JSON = Path(__file__).parent.parent / "forward_passes_flat.json"
assert _FORWARD_PASSES_FLAT_JSON.exists()

_FORWARD_PASSES_NESTED_JSON = (
    Path(__file__).parent.parent / "forward_passes_nested.json"
)
assert _FORWARD_PASSES_NESTED_JSON.exists()

_FLAT_DATASETS = Path(__file__).parent.parent / "flat_datasets"
assert _FLAT_DATASETS.exists()

_NESTED_DATASETS = Path(__file__).parent.parent / "nested_datasets"
assert _NESTED_DATASETS.exists()
