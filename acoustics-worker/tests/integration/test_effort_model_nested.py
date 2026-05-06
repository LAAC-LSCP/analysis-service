from analysis_service_core.testing.mixins import EffortModelTestBase

from src.core.effort_model import AcousticsEffortModel
from tests.integration.conftest import (
    _FORWARD_PASSES_NESTED_JSON,
    _NESTED_DATASETS,
    config_mock,
)


class TestAcousticsEffortModelNestedDataset(EffortModelTestBase):
    effort_model_cls = AcousticsEffortModel
    datasets_dir = _NESTED_DATASETS
    expected_forward_passes_json = _FORWARD_PASSES_NESTED_JSON
    config = config_mock
