from datetime import date
from typing import Any, Dict

from analysis_service_core.src.metannots import MetannotsFactory
from analysis_service_core.src.redis.commands import RunTask


class ALICEMetannotsFactory(MetannotsFactory):
    def get_default_values(self) -> Dict[str, Any]:
        return {
            "segmentation": "alice",
            "segmentation_type": "permissive",
            "method": "automated",
            "annotation_algorithm_name": "ALICE",
            "annotation_algorithm_publication": (
                "Lavechin, M., Bousbib, R., Bredin, H., Dupoux, E., & Cristia, A. "
                "(2020). An open-source voice type classifier for child-centered "
                "daylong recordings. Interspeech. Online open access: "
                "https://www.isca-archive.org/interspeech_2020/"
                "lavechin20_interspeech.pdf"
            ),
            "annotation_algorithm_version": "latest",
            "annotation_algorithm_repo": "https://github.com/orasanen/ALICE/",
            "date_annotation": date.today().isoformat(),
            "has_speaker_type": "Y",
        }

    def get_task_values(self, run_task: RunTask) -> Dict[str, Any]:
        return {}
