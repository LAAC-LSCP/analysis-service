from pathlib import Path

from analysis_service_core.src.redis.commands import Operation
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelE2ETestBase

_DUMMY_DIR = Path(__file__).parents[1]


class TestVTCE2E(ModelE2ETestBase):
    queue_name = QueueName.RUN_VTC
    operation = Operation.RUN_VTC
    dockerfile = Path(__file__).parents[2] / "vtc-worker" / "Dockerfile"
    datasets_dir = _DUMMY_DIR / "dummy_datasets"
    echolalia_dir = _DUMMY_DIR / "dummy_echolalia_folder"
    DATASET_UID = "d34200f0-07dc-48e7-8508-8436c5b20ed6"
    worker_env = {
        "VTC_FOLDER": "/app/voice_type_classifier",
        "VTC_DEVICE": "cpu",
        "CONDA_ENV_NAME": "pyannote",
        "CONDA_ACTIVATE_FILE": "/opt/conda/bin/activate",
    }
