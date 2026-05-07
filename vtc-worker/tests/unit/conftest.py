import shutil
from pathlib import Path

import pytest

CURRENT_FOLDER: Path = Path(__file__).parent
FLAT_RECORDINGS_DIR = (CURRENT_FOLDER / ".." / "flat_dataset").resolve()
NESTED_RECORDINGS_DIR = (CURRENT_FOLDER / ".." / "nested_dataset").resolve()


@pytest.fixture
def flat_dataset_tmp(tmp_path_factory: pytest.TempPathFactory):
    dest = tmp_path_factory.mktemp("flat_dataset")
    shutil.copytree(FLAT_RECORDINGS_DIR, dest, dirs_exist_ok=True)

    return dest


@pytest.fixture
def nested_dataset_tmp(tmp_path_factory: pytest.TempPathFactory):
    dest = tmp_path_factory.mktemp("nested_dataset")
    shutil.copytree(NESTED_RECORDINGS_DIR, dest, dirs_exist_ok=True)

    return dest
