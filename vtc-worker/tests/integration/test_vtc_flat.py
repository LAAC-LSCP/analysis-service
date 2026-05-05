from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelIntegrationTestBase

from tests.integration.conftest import _FLAT_DATASETS, mock_config
from tests.integration.effort_model_mock import VTCEffortModelMock
from tests.integration.vtc_mock import VTC_Mock


class TestVTCFlatDataset(ModelIntegrationTestBase):
    model_cls = VTC_Mock
    effort_model_cls = VTCEffortModelMock

    queue_name = QueueName.RUN_VTC
    config = mock_config

    datasets_dir = _FLAT_DATASETS
