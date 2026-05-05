from pathlib import Path

from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mocks import ConfigMock
from analysis_service_core.testing.mixins import ModelIntegrationTestBase

from tests.integration.conftest import _FLAT_DATASETS
from tests.integration.alice_mock import ALICEMock
from tests.integration.effort_model_mock import ALICEEffortModelMock


class TestALICEFlatDataset(ModelIntegrationTestBase):
    model_cls = ALICEMock
    effort_model_cls = ALICEEffortModelMock

    queue_name = QueueName.RUN_VTC

    datasets_dir = _FLAT_DATASETS

    def make_config(self, temp_dataset: Path) -> ConfigMock:
        return ConfigMock(overrides={
            "ALICE_FOLDER": temp_dataset / "alice_folder",
        })
