from pathlib import Path
from typing import Dict, Optional, TypeAlias

from src.core.effort_model import W2V2EffortModel

FileEfforts: TypeAlias = Dict[Path, int]


class W2V2EffortModelMock(W2V2EffortModel):
    _file_efforts: FileEfforts
    _default_file_size: int

    def __init__(
        self,
        file_efforts: Optional[FileEfforts] = None,
        default_file_size: int = 16_000,
    ):
        self._file_efforts = file_efforts or {}
        self._default_file_size = default_file_size

    def _bytes_per_second(self, file: Path) -> float:
        return self._file_efforts.get(file, self._default_file_size)
