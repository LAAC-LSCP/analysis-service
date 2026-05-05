from analysis_service_core.testing.mixins import EffortModelTestBase

from tests.integration.conftest import (
    _FLAT_DATASETS,
    _FORWARD_PASSES_FLAT_JSON,
    config_mock,
)
from tests.integration.effort_model_mock import VTC2EffortModelMock


class TestVTC2EffortModelFlatDataset(EffortModelTestBase):
    effort_model_cls = VTC2EffortModelMock
    datasets_dir = _FLAT_DATASETS
    expected_forward_passes_json = _FORWARD_PASSES_FLAT_JSON
    config = config_mock
