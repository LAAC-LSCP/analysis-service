from datetime import date
from typing import Any, Dict

from analysis_service_core.src.metannots import MetannotsFactory
from analysis_service_core.src.redis.commands import RunTask


class W2V2MetannotsFactory(MetannotsFactory):
    def get_default_values(self) -> Dict[str, Any]:
        return {
            "segmentation": "w2v2",
            "segmentation_type": "permissive",
            "method": "automated",
            "annotation_algorithm_name": "W2V2",
            "annotation_algorithm_publication": (
                "Zhang, T., Suresh, M., Warlaumont, "
                "A., Hitczenko, K., Cristia, A., & Cychosz, M. (2025). Employing "
                "self-supervised learning models for cross-linguistic child speech "
                "maturity classification."
            ),
            "annotation_algorithm_version": "latest",
            "annotation_algorithm_repo": "https://github.com/arxaqapi/speech-maturity",
            "date_annotation": date.today().isoformat(),
            "has_speaker_type": "N",
        }

    def get_task_values(self, run_task: RunTask) -> Dict[str, Any]:
        return {}
