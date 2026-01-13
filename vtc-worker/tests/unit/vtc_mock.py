from pathlib import Path

from src.core.vtc import VTC


class VTC_Mock(VTC):
    """
    Test double for VTC
    """

    def _run_subprocess(self, _: str, output_dir: Path, file: Path):
        # Here `output_dir` doubles as the present working directory
        # in the subprocess call, which for VTC, is where the outputs are
        vtc_base_dir = output_dir / "output_voice_type_classifier"
        vtc_output_dir = vtc_base_dir / file.stem

        vtc_output_dir.mkdir(parents=True, exist_ok=True)

        self._create_rttm_files(vtc_output_dir, file)

    def _create_rttm_files(self, vtc_output_dir: Path, file: Path) -> None:
        for f_name in [
            "all.rttm",
            "CHI.rttm",
            "FEM.rttm",
            "KCHI.rttm",
            "MAL.rttm",
            "SPEECH.rttm",
        ]:
            (vtc_output_dir / f_name).write_text(
                f"SPEAKER {file.stem} 0 0.000 0.000 <NA> <NA> <NA> <NA> <NA>"
            )
