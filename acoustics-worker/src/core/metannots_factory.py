from datetime import date
from typing import Any, Dict

from analysis_service_core.src.metannots import MetannotsFactory
from analysis_service_core.src.redis.commands import RunTask


class AcousticsMetannotsFactory(MetannotsFactory):
    def get_default_values(self) -> Dict[str, Any]:
        return {
            "segmentation": "acoustics",
            "segmentation_type": "permissive",
            "method": "automated",
            "annotation_algorithm_name": "Acoustics",
            "annotation_algorithm_publication": (
                "Gautheron, L., Rochat, N., & Cristia, A. (2022). Managing, storing, "
                "and sharing long-form recordings and their annotations. Language "
                "Resources and Evaluation."
            ),
            "annotation_algorithm_version": "latest",
            "annotation_algorithm_repo": "https://github.com/LAAC-LSCP/ChildProject",
            "date_annotation": date.today().isoformat(),
            "has_speaker_type": "Y",
        }

    def get_task_values(self, run_task: RunTask) -> Dict[str, Any]:
        return {}
