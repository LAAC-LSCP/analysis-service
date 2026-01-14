from pathlib import Path

from src.core.alice import ALICE


class ALICE_Mock(ALICE):
    """
    Test double for ALICE
    """

    def _run_subprocess(self, _: str, alice_dir: Path, file: Path) -> int:
        # Here `output_dir` doubles as the present working directory
        # in the subprocess call, which for ALICE, is where the outputs are
        self._create_outputs(alice_dir, file)

        return 0

    def _create_outputs(self, alice_dir: Path, _: Path) -> None:
        (alice_dir / "ALICE_output.txt").write_text(
            "FileID   phonemes        syllables       words\n"
            "1_1     117     56      36"
        )
        (alice_dir / "ALICE_output_utterances.txt").write_text(
            "/app/ALICE/tmp_data/short/1_1_0000005080_0000015540.wav 15.12   \
7.41    4.77"
        )
        (alice_dir / "diarization_output.rttm").write_text(
            "SPEAKER 1_1 1 0.508 1.046 <NA> <NA> FEM <NA> <NA>"
        )
