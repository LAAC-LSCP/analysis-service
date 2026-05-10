from pathlib import Path
from typing import Dict
from uuid import UUID

from analysis_service_core.src.redis.commands import Operation
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelE2ETestBase

from src.core.effort_model import AcousticsEffortModel

TESTS = Path(__file__).parents[1]
DOCKERFILE = TESTS.parent / "Dockerfile.dev"

assert DOCKERFILE.exists()


class TestAcousticsE2E(ModelE2ETestBase):
    queue_name = QueueName.RUN_ACOUSTICS
    operation = Operation.RUN_ACOUSTICS
    dockerfile = DOCKERFILE
    datasets_dir = TESTS / "e2e_datasets"
    echolalia_dir = TESTS / "echolalia_folder"
    extra_volume_mounts = [(TESTS.parent / "src", "/app/src")]
    DATASET_UID = UUID("d34200f0-07dc-48e7-8508-8436c5b20ed6")
    worker_env: Dict = {}
    TEST_IDEMPOTENCY = True
    effort_model_cls = AcousticsEffortModel
