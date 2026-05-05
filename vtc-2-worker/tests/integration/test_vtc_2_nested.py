from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelIntegrationTestBase

from tests.integration.conftest import _NESTED_DATASETS, config_mock
from tests.integration.effort_model_mock import VTC2EffortModelMock
from tests.integration.vtc_2_mock import VTC2Mock


class TestVTC2NestedDataset(ModelIntegrationTestBase):
    model_cls = VTC2Mock
    effort_model_cls = VTC2EffortModelMock

    queue_name = QueueName.RUN_VTC
    config = config_mock

    datasets_dir = _NESTED_DATASETS
