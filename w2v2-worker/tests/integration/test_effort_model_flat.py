from analysis_service_core.testing.mixins import EffortModelTestBase

from tests.integration.conftest import (
    _FLAT_DATASET,
    _FORWARD_PASSES_FLAT_JSON,
    config_mock,
)
from tests.integration.effort_model_mock import W2V2EffortModelMock


class TestW2V2EffortModelFlatDataset(EffortModelTestBase):
    effort_model_cls = W2V2EffortModelMock
    datasets_dir = _FLAT_DATASET
    expected_forward_passes_json = _FORWARD_PASSES_FLAT_JSON
    config = config_mock
