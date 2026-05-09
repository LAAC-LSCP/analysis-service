from analysis_service_core.testing.mixins import EffortModelTestBase

from tests.integration.conftest import (
    _FORWARD_PASSES_NESTED_JSON,
    _NESTED_DATASET,
    config_mock,
)
from tests.integration.effort_model_mock import W2V2EffortModelMock


class TestW2V2EffortModelNestedDataset(EffortModelTestBase):
    effort_model_cls = W2V2EffortModelMock
    datasets_dir = _NESTED_DATASET
    expected_forward_passes_json = _FORWARD_PASSES_NESTED_JSON
    config = config_mock
