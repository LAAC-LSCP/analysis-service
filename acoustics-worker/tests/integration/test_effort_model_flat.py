from analysis_service_core.testing.mixins import EffortModelTestBase

from src.core.effort_model import AcousticsEffortModel
from tests.integration.conftest import (
    _FLAT_DATASETS,
    _FORWARD_PASSES_FLAT_JSON,
    config_mock,
)


class TestAcousticsEffortModelFlatDataset(EffortModelTestBase):
    effort_model_cls = AcousticsEffortModel
    datasets_dir = _FLAT_DATASETS
    expected_forward_passes_json = _FORWARD_PASSES_FLAT_JSON
    config = config_mock
