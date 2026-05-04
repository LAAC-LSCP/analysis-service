from pathlib import Path

from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelIntegrationTestBase
from analysis_service_core.testing.mocks import ConfigMock

from tests.integration.conftest import _FLAT_DATASETS
from tests.integration.effort_model_mock import VTCEffortModelMock
from tests.integration.vtc_mock import VTC_Mock


class TestVTCFlatDataset(ModelIntegrationTestBase):
    model_cls = VTC_Mock
    effort_model_cls = VTCEffortModelMock

    queue_name = QueueName.RUN_VTC
    config = ConfigMock(
        overrides={
            "VTC_FOLDER": Path("/temp"),
            "VTC_DEVICE": "cpu",
            "CONDA_ACTIVATE_FILE": "",
            "CONDA_ENV_NAME": "",
        }
    )

    datasets_dir = _FLAT_DATASETS
