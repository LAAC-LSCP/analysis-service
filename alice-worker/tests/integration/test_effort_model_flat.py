from analysis_service_core.testing.mixins import EffortModelTestBase

from tests.integration.conftest import _FLAT_DATASETS, _FORWARD_PASSES_FLAT_JSON, flat_config_mock
from tests.integration.effort_model_mock import ALICEEffortModelMock


class TestALICEEffortModelFlatDataset(EffortModelTestBase):
    effort_model_cls = ALICEEffortModelMock
    datasets_dir = _FLAT_DATASETS
    expected_forward_passes_json = _FORWARD_PASSES_FLAT_JSON
    config = flat_config_mock
