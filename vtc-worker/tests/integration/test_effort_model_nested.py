from analysis_service_core.testing.mixins import EffortModelTestBase

from tests.integration.conftest import (
    _FORWARD_PASSES_NESTED_JSON,
    _NESTED_DATASETS,
    mock_config,
)
from tests.integration.effort_model_mock import VTCEffortModelMock


class TestVTCEffortModelNestedDataset(EffortModelTestBase):
    effort_model_cls = VTCEffortModelMock
    datasets_dir = _NESTED_DATASETS
    expected_forward_passes_json = _FORWARD_PASSES_NESTED_JSON
    config = mock_config
