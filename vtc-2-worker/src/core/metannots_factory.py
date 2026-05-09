from datetime import date
from typing import Any, Dict

from analysis_service_core.src.metannots import MetannotsFactory
from analysis_service_core.src.redis.commands import RunTask


class VTC2MetannotsFactory(MetannotsFactory):
    def get_default_values(self) -> Dict[str, Any]:
        return {
            "segmentation": "vtc-2",
            "segmentation_type": "permissive",
            "method": "automated",
            "annotation_algorithm_name": "VTC 2",
            "annotation_algorithm_publication": (
                "Charlot, T., Kunze, T., Poli, M., Cristia, A., Dupoux, E., "
                "& Lavechin, M. (2026). BabyHuBERT: Multilingual Self-Supervised "
                "Learning for Segmenting Speakers in Child-Centered Long-Form "
                "Recordings. arXiv [Eess.AS]. Retrieved from "
                "http://arxiv.org/abs/2509.15001"
            ),
            # NOTE: change this when one day updating to latest
            "annotation_algorithm_version": "Jan 6 2026 version",
            "annotation_algorithm_repo": "https://github.com/LAAC-LSCP/VTC",
            "date_annotation": date.today().isoformat(),
            "has_speaker_type": "Y",
        }

    def get_task_values(self, run_task: RunTask) -> Dict[str, Any]:
        return {}
