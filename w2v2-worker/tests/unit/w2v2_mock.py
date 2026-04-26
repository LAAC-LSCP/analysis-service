import csv
import json
from pathlib import Path
from typing import List, Tuple

from analysis_service_core.testing.mocks.pubsub import PubSubMock

from src.core.w2v2 import W2V2


class W2V2Mock(W2V2):
    def __init__(
        self,
        queue,
        config,
        pubsub=PubSubMock(),
        effort_model=None,
        skip_moving_files=False,
    ):
        super().__init__(queue, config, pubsub, effort_model, skip_moving_files)

    def _create_samples_csv(
        self, dataset_dir: Path, output_dir: Path
    ) -> Tuple[int, Path]:
        output_csv = output_dir / "chi_vocs.csv"

        output_csv.touch()
        return 0, output_csv

    def _chunkify(
        self, dataset_dir: Path, output_dir: Path, samples_csv: Path
    ) -> Tuple[int, Path]:
        # this one is harder to mimick, as it depends on the audio. Will just create 2
        # chunks per audio file for now
        conv_std_recs = dataset_dir / "recordings" / "converted" / "standard"

        chunks = output_dir / "chunks"
        chunks_chunks = chunks / "chunks"
        chunks_chunks.mkdir(parents=True, exist_ok=True)

        (chunks / "segments.csv").touch()

        for f in self._get_chunks(chunks_chunks, conv_std_recs):
            f.touch()

        return 0, chunks

    def _get_chunks(self, chunks: Path, converted_recs: Path) -> List[Path]:
        start_ends: List[Tuple[int, int]] = [(1000, 1050), (2000, 2050)]

        recs = [f for f in converted_recs.rglob("**.wav") if f.is_file()]
        rel_paths = [f.relative_to(converted_recs) for f in recs]
        parts_list = [
            f.with_suffix("").parts + (str(start), str(end))
            for f in rel_paths
            for start, end in start_ends
        ]

        return [
            (chunks / "_".join(parts)).with_suffix(suffix)
            for parts in parts_list
            for suffix in [".wav", ".mp3"]
        ]

    def _run_gen_json(
        self, w2v2_dir: Path, chunks_dir: Path, output_dir: Path
    ) -> Tuple[int, Path]:
        json_file = output_dir / "audio_chunks.json"

        json_file.parent.mkdir(parents=True, exist_ok=True)
        json_file.touch()

        # mimick W2V2's code
        chunks_audio = chunks_dir / "chunks"
        wav_files = list(chunks_audio.glob("*.wav"))

        data = {f.stem: {"wav": str(f.resolve()), "label": ""} for f in wav_files}

        with open(json_file, "w") as f:
            json.dump(data, f, indent=4)

        return 0, json_file

    def _set_hparams(self, w2v2_dir: Path) -> None:
        pass

    def _run_w2v2(
        self, w2v2_dir: Path, audio_chunks_json: Path, output_dir: Path
    ) -> Tuple[int, Path]:
        w2v2_output_dir = output_dir / "w2v2_outputs"
        w2v2_output_dir.mkdir(exist_ok=True, parents=True)

        chunks: dict
        with open(audio_chunks_json, "r") as f:
            chunks = json.load(f)

        predictions_csv = w2v2_output_dir / "predictions.csv"
        with open(predictions_csv, "w") as f:
            f.write("id,prediction,prediction_class_name\n")
            for chunk_id in chunks:
                f.write(f"{chunk_id},0,Canonical\n")

        return 0, w2v2_output_dir

    def _split_output(
        self, dataset_dir: Path, w2v2_output_dir: Path, output_dir: Path
    ) -> int:
        predictions_csv = w2v2_output_dir / "predictions.csv"
        output_folder = Path(output_dir) / "output" / "raw"
        output_folder.mkdir(parents=True, exist_ok=True)
        recording_filenames = set()

        with open(predictions_csv, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                chunk_id = row["id"]
                rec = "_".join(chunk_id.split("_")[:-2]) + ".wav"
                recording_filenames.add(rec)

        for rec in recording_filenames:
            output = (output_folder / rec).with_suffix(".csv")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.touch()

        return 0
