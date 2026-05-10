from pathlib import Path
from typing import Dict
from uuid import UUID

from analysis_service_core.src.redis.commands import Operation
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelE2ETestBase

from src.core.effort_model import VTC2EffortModel

TESTS = Path(__file__).parents[1]
DOCKERFILE = TESTS.parent / "Dockerfile.dev"

assert DOCKERFILE.exists()


class TestVTC2E2E(ModelE2ETestBase):
    queue_name = QueueName.RUN_VTC_2
    operation = Operation.RUN_VTC_2
    dockerfile = DOCKERFILE
    datasets_dir = TESTS / "e2e_datasets"
    echolalia_dir = TESTS / "echolalia_folder"
    extra_volume_mounts = [(TESTS.parent / "src", "/app/src")]
    DATASET_UID = UUID("d34200f0-07dc-48e7-8508-8436c5b20ed6")
    worker_env: Dict = {
        "VTC_2_FOLDER": "/app/VTC",
        "VTC_2_DEVICE": "cpu",
    }
    TEST_IDEMPOTENCY = True
    effort_model_cls = VTC2EffortModel
