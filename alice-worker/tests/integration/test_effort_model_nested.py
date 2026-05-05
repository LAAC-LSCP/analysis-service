from analysis_service_core.testing.mixins import EffortModelTestBase

from tests.integration.conftest import _NESTED_DATASETS, _FORWARD_PASSES_NESTED_JSON, nested_config_mock
from tests.integration.effort_model_mock import ALICEEffortModelMock


class TestALICEEffortModelNestedDataset(EffortModelTestBase):
    effort_model_cls = ALICEEffortModelMock
    datasets_dir = _NESTED_DATASETS
    expected_forward_passes_json = _FORWARD_PASSES_NESTED_JSON
    config = nested_config_mock
