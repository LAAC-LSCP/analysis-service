from pathlib import Path
from typing import Dict, Optional, TypeAlias

from src.core.effort_model import _SAMPLING_RATE, ALICEEffortModel
from analysis_service_core.src.config import Config

FileEfforts: TypeAlias = Dict[Path, int]


class ALICEEffortModelMock(ALICEEffortModel):
    _file_efforts: FileEfforts
    _default_file_size: int

    def __init__(
        self,
        config: Config,
        file_efforts: Optional[FileEfforts] = None,
        default_file_size: int = 16_000,
    ):
        self._file_efforts = file_efforts or {}
        self._default_file_size = default_file_size

        super().__init__(config)

    def _bytes_per_second(self, file: Path) -> float:
        return self._file_efforts.get(file, self._default_file_size) / _SAMPLING_RATE
