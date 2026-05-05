import os
import shutil
import subprocess
from pathlib import Path
from typing import Set
from uuid import UUID
import pandas as pd
from collections import defaultdict

from analysis_service_core.src.effort_model import InputGroup, PassOutputGroup
from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.model import ModelPlugin

from src.core.effort_model import ALICEEffortModel

logger = LoggerFactory.get_logger(__name__)


class ALICE(ModelPlugin):

    SPEAKER_TYPE_TRANSLATION = defaultdict(
        lambda: "NA", {"CHI": "OCH", "KCHI": "CHI", "FEM": "FEM", "MAL": "MAL", "OCH": "OCH"}
    )

    def run_model(self, dataset_dir: Path, output_dir: Path) -> None:
        output_dir = output_dir / "output"

        conv_std_recs = self._get_conv_std_recs(dataset_dir)

        if not conv_std_recs.exists():
            raise ValueError(
                f"Recordings directory at '{conv_std_recs}' does not exist"
            )

        audio_files = self._get_audio_files(conv_std_recs)

        for file in audio_files:
            self._run_alice_on_audio_file(conv_std_recs, output_dir, file)
            self.report_progress(dataset_dir, task_id)

    def _run_alice_on_audio_file(
        self, recordings_dir: Path, final_output_dir: Path, file: Path
    ) -> None:
        logger.info(f"Running ALICE on {recordings_dir!s}")
        executable: Path = self.alice_dir / "run_ALICE.sh"

        device_str: str = ""
        if self.config.get("ALICE_DEVICE") == "gpu":
            device_str = "gpu"

        bash_script = f"""
        source {self.config.get("CONDA_ACTIVATE_FILE")}
        conda activate {self.config.get("CONDA_ENV_NAME")}
        {str(executable)} {str(file)} {device_str}
        """

        self._run_subprocess(bash_script, self.alice_dir, file)

    def _run_subprocess(self, bash_script: str, alice_dir: Path, file: Path) -> int:
        # NOTE: ALICE has a quirk that it cannot run if your PWD is not the
        # ALICE folder itself
        result = subprocess.run(
            ["bash", "-c", bash_script],
            cwd=alice_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            logger.info(f"Successfully ran ALICE on '{file!s}'")
        else:
            logger.error(f"Error running ALICE on '{file!s}: {result.stderr}")

        return result.returncode

    def postprocess(
        self,
        dataset_dir: Path,
        output_dir: Path,
        pogroup: PassOutputGroup,
        igroup: InputGroup,
    ) -> None:
        conv_std_recs = ALICEEffortModel.get_conv_std_recs(dataset_dir)
        audio_file = igroup[0]
        rel_path: Path = audio_file.relative_to(conv_std_recs)
        final_output_dir = output_dir / "output"

        rel_path_dir = rel_path.parent
        base_name = rel_path.stem

        raw_folder = output_dir / rel_path_dir / "raw"

        if not raw_folder.exists():
            raw_folder.mkdir(parents=True, exist_ok=True)

        utterance_output = self.alice_dir / "ALICE_output_utterances.txt"
        general_output = self.alice_dir / "ALICE_output.txt"
        diarization_output = self.alice_dir / "diarization_output.rttm"

        output = self.merge_output(utterance_output, diarization_output)

        output.to_csv(raw_folder / f"{base_name}.csv", index=False)

        if diarization_output.exists():  # This doesn't always exist??
            os.remove(diarization_output)

        if utterance_output.exists(): 
            os.remove(utterance_output)

        if general_output.exists():
            os.remove(general_output)

    @property
    def alice_dir(self) -> Path:
        return self.config.get("ALICE_FOLDER")

    def merge_output(self, alice_file: Path, rttm_file: Path) -> pd.DataFrame:
        adf = pd.read_csv(
            alice_file,
            sep=r"\s",
            names=["file", "phonemes", "syllables", "words"],
            engine="python",
        )

        matches = adf["file"].str.extract(
            r"^(.*)_(?:0+)?([0-9]{1,})_(?:0+)?([0-9]{1,})\.wav$"
        )
        adf["recording_filename"] = matches[0]
        adf["segment_onset"] = matches[1].astype(int) / 10
        adf["segment_offset"] = matches[2].astype(int) / 10

        adf.drop(columns=["recording_filename", "file"], inplace=True)

        vdf = pd.read_csv(
            rttm_file,
            sep=" ",
            names=[
                "type",
                "file",
                "chnl",
                "tbeg",
                "tdur",
                "ortho",
                "stype",
                "name",
                "conf",
                "unk",
            ],
            dtype={'type': str, "file" : str, 'stype':str}
        )

        vdf["segment_onset"] = vdf["tbeg"].mul(1000).round().astype(int)
        vdf["segment_offset"] = (vdf["tbeg"] + vdf["tdur"]).mul(1000).round().astype(int)
        vdf["speaker_type"] = vdf["name"].map(self.SPEAKER_TYPE_TRANSLATION)

        vdf.drop(
            [
                "type",
                "file",
                "chnl",
                "tbeg",
                "tdur",
                "ortho",
                "stype",
                "name",
                "conf",
                "unk",
            ],
            axis=1,
            inplace=True,
        )

        df = vdf.merge(
            adf,
            how="outer",
            on=['segment_onset', 'segment_offset'],
        )

        return df
