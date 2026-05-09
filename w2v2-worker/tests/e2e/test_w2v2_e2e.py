from pathlib import Path
from typing import Dict
from uuid import UUID

from analysis_service_core.src.redis.commands import Operation
from analysis_service_core.src.redis.queue import QueueName
from analysis_service_core.testing.mixins import ModelE2ETestBase

from src.core.effort_model import W2V2EffortModel

TESTS = Path(__file__).parents[1]
DOCKERFILE = TESTS.parent / "Dockerfile.dev"

assert DOCKERFILE.exists()


class TestW2V2E2E(ModelE2ETestBase):
    queue_name = QueueName.RUN_W2V2
    operation = Operation.RUN_W2V2
    dockerfile = DOCKERFILE
    datasets_dir = TESTS / "e2e_datasets"
    echolalia_dir = TESTS / "echolalia_folder"
    extra_volume_mounts = [
        (TESTS.parent / "src", "/app/src"),
        (TESTS.parent / "src" / "infer.py", "/app/speech-maturity/scripts/infer.py"),
    ]
    DATASET_UID = UUID("d34200f0-07dc-48e7-8508-8436c5b20ed6")
    worker_env: Dict = {
        "CHUNKIFY_THREADS": 8,
        "W2V2_FOLDER": "/app/speech-maturity",
        "W2V2_DEVICE": "cpu",
        "NUM_WORKERS": 2,
        "BATCH_SIZE": 32,
    }
    TEST_IDEMPOTENCY = True
    effort_model_cls = W2V2EffortModel
