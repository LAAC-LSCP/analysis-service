from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelIntegrationTestBase

from tests.integration.conftest import _NESTED_DATASETS, config_mock
from tests.integration.effort_model_mock import W2V2EffortModelMock
from tests.integration.w2v2_mock import W2V2Mock


class TestW2V2NestedDataset(ModelIntegrationTestBase):
    model_cls = W2V2Mock
    effort_model_cls = W2V2EffortModelMock

    queue_name = QueueName.RUN_W2V2

    datasets_dir = _NESTED_DATASETS
    config = config_mock
