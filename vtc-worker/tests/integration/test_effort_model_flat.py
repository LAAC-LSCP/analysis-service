from analysis_service_core.testing.mixins import EffortModelTestBase

from tests.integration.conftest import (
    _FLAT_DATASETS,
    _FORWARD_PASSES_FLAT_JSON,
    mock_config,
)
from tests.integration.effort_model_mock import VTCEffortModelMock


class TestVTCEffortModelFlatDataset(EffortModelTestBase):
    effort_model_cls = VTCEffortModelMock
    datasets_dir = _FLAT_DATASETS
    expected_forward_passes_json = _FORWARD_PASSES_FLAT_JSON
    config = mock_config
