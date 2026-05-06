from pathlib import Path

import pandas as pd
import pytest

_DATA = Path(__file__).parent / "data"


@pytest.fixture
def utterances_file() -> Path:
    return _DATA / "utterances.txt"


@pytest.fixture
def diarization_file() -> Path:
    return _DATA / "diarization.rttm"


@pytest.fixture
def expected_merged() -> pd.DataFrame:
    return pd.read_csv(
        _DATA / "expected_merged.csv",
        dtype={"speaker_type": "string"},
    )
