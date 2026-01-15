import os
import shutil
import subprocess
from contextlib import ExitStack
from pathlib import Path
from typing import Tuple

from analysis_service_core.src.logger import LoggerFactory
from analysis_service_core.src.model import ModelPlugin
from ruamel.yaml import YAML

logger = LoggerFactory.get_logger(__name__)

CURRENT_DIR: Path = Path(__file__).parent


class W2V2(ModelPlugin):
    def run_model(self, dataset_dir: Path, output_dir: Path) -> None:
        if not output_dir.exists():
            output_dir.mkdir(exist_ok=True, parents=True)

        with ExitStack() as stack:
            return_code, samples_csv = self._create_samples_csv(dataset_dir, output_dir)
            stack.callback(self._cleanup_samples, samples_csv)
            if return_code != 0:
                return

            return_code, chunks_dir = self._chunkify(
                dataset_dir, output_dir, samples_csv
            )
            stack.callback(self._cleanup_chunks, chunks_dir)
            if return_code != 0:
                return

            w2v2_dir = self.config.get("W2V2_FOLDER")
            return_code, audio_chunks_json = self._run_gen_json(
                w2v2_dir, chunks_dir, output_dir
            )
            stack.callback(self._cleanup_chunks_json, audio_chunks_json)
            if return_code != 0:
                return

            try:
                self._set_hparams(w2v2_dir)
            except Exception as e:
                logger.error(f"Failed to set hparams: {e}")
                return

            return_code, w2v2_output_dir = self._run_w2v2(
                w2v2_dir, audio_chunks_json, output_dir
            )
            stack.callback(self._cleanup_w2v2_output, w2v2_output_dir)
            if return_code != 0:
                return

            return_code = self._split_output(dataset_dir, w2v2_output_dir, output_dir)

            return

        return

    def _create_samples_csv(
        self, dataset_dir: Path, output_dir: Path
    ) -> Tuple[int, Path]:
        output_csv: Path = output_dir / "chi_vocs.csv"
        sample_chi_vocs_py: Path = CURRENT_DIR / "sample_chi_vocs.py"

        cmd = [
            "python",
            str(sample_chi_vocs_py),
            "--dataset-path",
            str(dataset_dir),
            "--output-path",
            str(output_csv),
        ]

        logger.info(f"Creating samples in '{str(dataset_dir)}'")
        result = subprocess.run(cmd, cwd=dataset_dir, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Successfully created samples in '{str(dataset_dir)}'")
        else:
            logger.error(
                f"Error creating samples in '{str(dataset_dir)}: {result.stderr}"
            )

        return result.returncode, output_csv

    def _chunkify(
        self, dataset_dir: Path, output_dir: Path, samples_csv: Path
    ) -> Tuple[int, Path]:
        create_chunks: Path = CURRENT_DIR / "create_chunks.py"
        chunks_dir: Path = output_dir / "chunks"

        cmd = [
            "python",
            str(create_chunks),
            "--dataset-path",
            str(dataset_dir),
            "--segments-path",
            str(samples_csv),
            "--destination-path",
            str(chunks_dir),
            "--threads",
            str(self.config.get("CHUNKIFY_THREADS")),
        ]

        logger.info(f"Creating chunks in '{str(chunks_dir)}'...")
        result = subprocess.run(cmd, cwd=dataset_dir, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Successfully created chunks in '{str(chunks_dir)}'")
        else:
            logger.error(
                f"Error creating chunks in dataset '{str(dataset_dir)}: {result.stderr}"
            )

        self._remove_mp3_files(chunks_dir / "chunks")

        return result.returncode, chunks_dir

    def _remove_mp3_files(self, dir: Path) -> None:
        files = [f for f in dir.rglob("*") if f.is_file() and f.suffix == ".mp3"]
        for f in files:
            f.unlink()

        return

    def _run_gen_json(
        self, w2v2_dir: Path, chunks_dir: Path, output_dir: Path
    ) -> Tuple[int, Path]:
        audio_chunks_json = output_dir / "audio_chunks.json"
        bash_script = f"""
uv run scripts/gen_json.py --audio {str(chunks_dir / "chunks")} \
--output {str(audio_chunks_json)}
        """
        w2v2_venv = w2v2_dir / ".venv"

        logger.info("Running gen_json.py...")
        result = subprocess.run(
            ["bash", "-c", bash_script],
            cwd=w2v2_dir,
            capture_output=True,
            text=True,
            env={
                "VIRTUAL_ENV": str(w2v2_venv),
                "PATH": f"{w2v2_venv}/bin:" + os.environ["PATH"],
            },
        )

        if result.returncode == 0:
            logger.info("Successfully ran gen_json.py")
        else:
            logger.error(
                f"Error running gen_json.py in folder '{str(w2v2_dir)}' with \
audio '{str(chunks_dir)}' and output '{str(output_dir)}': {result.stderr}"
            )

        return result.returncode, audio_chunks_json

    def _set_hparams(self, w2v2_dir: Path) -> None:
        logger.info("Setting hparams...")
        hparams = w2v2_dir / "hparams" / "hparams.yaml"

        yaml = YAML()
        data: dict
        with open(hparams) as f:
            data = yaml.load(f)

        batch_size = self.config.get("BATCH_SIZE")
        num_workers = self.config.get("NUM_WORKERS")

        data["dataloader_options"]["batch_size"] = batch_size
        data["dataloader_options"]["num_workers"] = num_workers

        data["valid_dataloader_options"]["batch_size"] = batch_size
        data["valid_dataloader_options"]["num_workers"] = num_workers

        data["test_dataloader_options"]["batch_size"] = batch_size
        data["test_dataloader_options"]["num_workers"] = num_workers

        with open(hparams, "w") as f:
            yaml.dump(data, f)

        logger.info("Done setting hparams")
        return

    def _run_w2v2(
        self, w2v2_dir: Path, audio_chunks_json: Path, output_dir: Path
    ) -> Tuple[int, Path]:
        w2v2_output_dir = output_dir / "w2v2_outputs"

        if not w2v2_output_dir.exists():
            w2v2_output_dir.mkdir(exist_ok=True, parents=True)

        bash_script = f"""
uv run scripts/infer.py hparams/hparams.yaml \
--output_folder {str(w2v2_output_dir)} \
--train_annotation {str(audio_chunks_json)} \
--valid_annotation {str(audio_chunks_json)} \
--test_annotation {str(audio_chunks_json)} \
--device {self.config.get("W2V2_DEVICE")}
        """
        w2v2_venv = w2v2_dir / ".venv"

        logger.info("Running w2v2 inference...")
        result = subprocess.run(
            ["bash", "-c", bash_script],
            cwd=w2v2_dir,
            capture_output=True,
            text=True,
            env={
                "VIRTUAL_ENV": str(w2v2_venv),
                "PATH": f"{w2v2_venv}/bin:" + os.environ["PATH"],
            },
        )

        if result.returncode == 0:
            logger.info("Successfully ran w2v2 inference")
        else:
            logger.error(
                f"Error running w2v2 inference in folder '{str(w2v2_dir)}' with \
audio chunks '{str(audio_chunks_json)}' and output '{str(w2v2_output_dir)}'.\n\
STDOUT:\n\
{result.stdout}\n\
STDERR:\n\
{result.stderr}"
            )

        return result.returncode, w2v2_output_dir

    def _split_output(
        self, dataset_dir: Path, w2v2_output_dir: Path, output_dir: Path
    ) -> int:
        split_output: Path = CURRENT_DIR / "split_output.py"

        cmd = [
            "python",
            str(split_output),
            "--dataset-path",
            str(dataset_dir),
            "--w2v2-predictions-csv",
            str(w2v2_output_dir / "predictions.csv"),
            "--output-path",
            str(output_dir / "output" / "raw"),
        ]

        logger.info(f"Splitting outputs for '{str(dataset_dir)}'")
        result = subprocess.run(cmd, cwd=dataset_dir, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Successfully split outputs in '{str(dataset_dir)}'")
        else:
            logger.error(
                f"Error splitting outputs '{str(dataset_dir)}: {result.stderr}"
            )

        return result.returncode

    def _cleanup_samples(self, samples_csv: Path) -> None:
        if samples_csv.exists():
            samples_csv.unlink()

    def _cleanup_chunks(self, chunks_dir: Path) -> None:
        if chunks_dir.exists():
            shutil.rmtree(chunks_dir)

    def _cleanup_chunks_json(self, audio_chunks_json: Path) -> None:
        if audio_chunks_json.exists():
            audio_chunks_json.unlink()

    def _cleanup_w2v2_output(self, w2v2_output_dir: Path) -> None:
        if w2v2_output_dir.exists():
            shutil.rmtree(w2v2_output_dir)
