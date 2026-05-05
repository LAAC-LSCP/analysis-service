from analysis_service_core.testing.mixins import EffortModelTestBase

from tests.integration.conftest import (
    _FORWARD_PASSES_NESTED_JSON,
    _NESTED_DATASETS,
    config_mock,
)
from tests.integration.effort_model_mock import VTC2EffortModelMock


class TestVTC2EffortModelNestedDataset(EffortModelTestBase):
    effort_model_cls = VTC2EffortModelMock
    datasets_dir = _NESTED_DATASETS
    expected_forward_passes_json = _FORWARD_PASSES_NESTED_JSON
    config = config_mock
