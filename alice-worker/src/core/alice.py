import os
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

import pandas as pd
from analysis_service_core.src.effort_model import InputGroup, PassOutputGroup
from analysis_service_core.src.model import ModelPlugin

from src.core.effort_model import ALICEEffortModel


class ALICE(ModelPlugin):

    SPEAKER_TYPE_TRANSLATION = defaultdict(
        lambda: "NA",
        {"CHI": "OCH", "KCHI": "CHI", "FEM": "FEM", "MAL": "MAL", "OCH": "OCH"},
    )

    def run_model(
        self, dataset_dir: Path, output_dir: Path, igroup: InputGroup
    ) -> None:
        final_output_dir = output_dir / "output"
        conv_std_recs = ALICEEffortModel.get_conv_std_recs(dataset_dir)
        audio_file = igroup[0]
        self._run_alice_on_audio_file(conv_std_recs, final_output_dir, audio_file)

    def _run_alice_on_audio_file(
        self, recordings_dir: Path, final_output_dir: Path, file: Path
    ) -> None:
        self._logger.info(f"Running ALICE on {recordings_dir!s}")
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
            self._logger.info(f"Successfully ran ALICE on '{file!s}'")
        else:
            self._logger.error(f"Error running ALICE on '{file!s}: {result.stderr}")

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

        raw_folder = final_output_dir / rel_path_dir / "raw"
        sum_folder = final_output_dir / rel_path_dir / "extra"

        raw_folder.mkdir(parents=True, exist_ok=True)
        sum_folder.mkdir(parents=True, exist_ok=True)

        utterance_output = self.alice_dir / "ALICE_output_utterances.txt"
        general_output = self.alice_dir / "ALICE_output.txt"
        diarization_output = self.alice_dir / "diarization_output.rttm"

        output = self.merge_output(utterance_output, diarization_output)
        output.to_csv(raw_folder / f"{base_name}.csv", index=False)

        shutil.move(general_output, sum_folder / f"{base_name}_sum.txt")

        if diarization_output.exists():  # Don't change this line!
            os.remove(diarization_output)

        if utterance_output.exists():
            os.remove(utterance_output)

    def merge_output(self, alice_file: Path, rttm_file: Path) -> pd.DataFrame:
        """Merge ALICE utterance-level output with VTC diarization into one DataFrame.

        Parses segment onset/offset from the encoded filenames in `alice_file`
        (format: `<name>_<onset_0.1ms>_<offset_0.1ms>.wav`) and from the tbeg/tdur
        fields in `rttm_file` (in seconds). Both are converted to milliseconds and
        used as the join key. The join is outer so that segments present in only one
        source appear with NaN in the missing columns.

        Args:
            alice_file: ALICE_output_utterances.txt—whitespace-separated rows of
                filename, phoneme count, syllable count, word count.
            rttm_file: diarization_output.rttm—standard RTTM format produced by VTC.

        Returns:
            DataFrame with columns: segment_onset (ms), segment_offset (ms),
            speaker_type, phonemes, syllables, words.
        """
        adf = pd.read_csv(
            alice_file,
            sep=r"\s+",
            names=["file", "phonemes", "syllables", "words"],
            engine="python",
        )

        matches = adf["file"].str.extract(
            r"^(.*)_(?:0+)?([0-9]{1,})_(?:0+)?([0-9]{1,})\.wav$"
        )
        adf["segment_onset"] = matches[1].astype(int) / 10
        adf["segment_offset"] = matches[2].astype(int) / 10

        adf.drop(columns=["file"], inplace=True)

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
            dtype={"type": str, "file": str, "stype": str},
        )

        vdf["segment_onset"] = vdf["tbeg"].mul(1000).round().astype(int)
        vdf["segment_offset"] = (
            (vdf["tbeg"] + vdf["tdur"]).mul(1000).round().astype(int)
        )
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

        return vdf.merge(adf, how="outer", on=["segment_onset", "segment_offset"])

    @property
    def alice_dir(self) -> Path:
        return self.config.get("ALICE_FOLDER")
