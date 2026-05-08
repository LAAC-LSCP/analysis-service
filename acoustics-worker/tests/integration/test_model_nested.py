from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelIntegrationTestBase
from analysis_service_core.testing.mocks import ConfigMock

from src.core.effort_model import AcousticsEffortModel
from tests.integration.acoustics_mock import AcousticsMock
from tests.integration.conftest import _NESTED_DATASETS


class TestAcousticsNestedDataset(ModelIntegrationTestBase):
    model_cls = AcousticsMock
    effort_model_cls = AcousticsEffortModel

    queue_name = QueueName.RUN_VTC

    datasets_dir = _NESTED_DATASETS
    config = ConfigMock()
