import shutil
from pathlib import Path

import pytest

CURRENT_FOLDER: Path = Path(__file__).parent
FLAT_RECORDINGS_DIR = (CURRENT_FOLDER / ".." / "recordings_dir_flat").resolve()
NESTED_RECORDINGS_DIR = (CURRENT_FOLDER / ".." / "recordings_dir_nested").resolve()


@pytest.fixture
def flat_recordings_tmp(tmp_path_factory: pytest.TempPathFactory):
    dest = tmp_path_factory.mktemp("flat_recordings")
    shutil.copytree(FLAT_RECORDINGS_DIR, dest, dirs_exist_ok=True)

    return dest


@pytest.fixture
def nested_recordings_tmp(tmp_path_factory: pytest.TempPathFactory):
    dest = tmp_path_factory.mktemp("nested_recordings")
    shutil.copytree(NESTED_RECORDINGS_DIR, dest, dirs_exist_ok=True)

    return dest
