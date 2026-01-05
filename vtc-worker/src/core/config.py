from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    echolalia_dir: Path
    datasets_dir: Path
    conda_activate_file: Path
    conda_env_name: str
