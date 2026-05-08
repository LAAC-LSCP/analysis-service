from pathlib import Path

import pandas as pd
import pytest

from src.core.alice import ALICE


@pytest.fixture
def alice(tmp_path) -> ALICE:
    from analysis_service_core.src.config import Config
    from analysis_service_core.src.redis.queue import QueueName
    from analysis_service_core.testing.mocks.pubsub import PubSubMock
    from analysis_service_core.testing.mocks.queue import QueueMock

    from tests.integration.effort_model_mock import ALICEEffortModelMock

    config = Config(check_required=False)
    config.set("ALICE_FOLDER", tmp_path)

    return ALICE(
        queue=QueueMock(QueueName.RUN_ALICE),
        config=config,
        effort_model=ALICEEffortModelMock(config=config),
        pubsub=PubSubMock(),
    )


def test_matched_row(alice: ALICE, utterances_file: Path, diarization_file: Path):
    result = alice.merge_output(utterances_file, diarization_file)
    matched = result[result["segment_onset"] == 508].iloc[0]

    assert matched["speaker_type"] == "FEM"
    assert matched["phonemes"] == pytest.approx(15.12)
    assert matched["syllables"] == pytest.approx(7.41)
    assert matched["words"] == pytest.approx(4.77)


def test_speaker_type_translation(
    alice: ALICE, utterances_file: Path, diarization_file: Path
):
    result = alice.merge_output(utterances_file, diarization_file)
    # KCHI in the RTTM should translate to CHI
    kchi_row = result[result["segment_onset"] == 3200].iloc[0]
    assert kchi_row["speaker_type"] == "CHI"


def test_unmatched_rttm_row_has_nan_alice_fields(
    alice: ALICE, utterances_file: Path, diarization_file: Path
):
    result = alice.merge_output(utterances_file, diarization_file)
    # CHI in the RTTM (onset=4500) has no matching utterance → outer join produces NaN
    unmatched = result[result["segment_onset"] == 4500].iloc[0]
    assert unmatched["speaker_type"] == "OCH"
    assert pd.isna(unmatched["phonemes"])
    assert pd.isna(unmatched["syllables"])
    assert pd.isna(unmatched["words"])


def test_full_output_matches_expected(
    alice: ALICE,
    utterances_file: Path,
    diarization_file: Path,
    expected_merged: pd.DataFrame,
):
    result = alice.merge_output(utterances_file, diarization_file)
    pd.testing.assert_frame_equal(
        result.reset_index(drop=True), expected_merged, check_dtype=False
    )
