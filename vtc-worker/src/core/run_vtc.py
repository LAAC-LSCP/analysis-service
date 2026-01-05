import shutil
import subprocess
from pathlib import Path
from typing import Set
from uuid import UUID

from src.core.config import Config
from src.core.file_formats import RecordingFormats

VTC_DIR: Path = (
    Path(__file__) / ".." / ".." / ".." / "vtc" / "voice-type-classifier"
).resolve()


def run_vtc(task_id: UUID, dataset_id_label: str, config: Config) -> None:
    dataset_dir = get_dataset_dir(config.datasets_dir, dataset_id_label)
    recordings_dir = dataset_dir / "recordings" / "converted"
    output_dir = get_task_output_dir(config.echolalia_dir, task_id, dataset_id_label)

    if not recordings_dir.exists():
        raise ValueError(f"Recordings directory at '{recordings_dir}' does not exist")

    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    audio_files = get_audio_files(recordings_dir)

    for file in audio_files:
        run_vtc_on_audio_file(config, recordings_dir, output_dir, file)

    return


def run_vtc_on_audio_file(
    config: Config, recordings_dir: Path, output_dir: Path, file: Path
) -> None:
    rel_path: Path = file.relative_to(recordings_dir)

    executable: Path = VTC_DIR / "apply.sh"

    bash_script = f"""
    source {config.conda_activate_file}
    conda activate {config.conda_env_name}
    {str(executable)} {str(file)} --device=gpu
    """

    run_subprocess(bash_script, output_dir, file)

    move_file(rel_path, output_dir, file)

    return


def move_file(rel_path: Path, output_dir: Path, input_file: Path) -> None:
    """
    VTC quirks to bear in mind:

    - VTC puts the output files into the same folder as the present working directory
    - Puts it under the folder "output_voice_type_classifier/[name of input file]"
    - In there you'll find various outputs. We want "all.rttm"
    """
    vtc_base_dir = output_dir / "output_voice_type_classifier"
    vtc_output_dir = vtc_base_dir / input_file.stem
    all_rttm = vtc_output_dir / "all.rttm"

    if not all_rttm.exists():
        print(f"WARNING: Expected output file {all_rttm} not found")
        return

    output_file = (output_dir / rel_path).resolve()
    output_file.parent.mkdir(parents=True, exist_ok=True)

    final_output = output_file.with_suffix(".rttm")
    all_rttm.rename(final_output)

    if vtc_base_dir.exists():
        shutil.rmtree(vtc_base_dir)

    return


def run_subprocess(bash_script: str, output_dir: Path, file: Path) -> None:
    # Note that vtc has a quirk that it puts outputs in the current working dir
    result = subprocess.run(
        bash_script, shell=True, cwd=output_dir, capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"Successfully ran VTC on '{str(file)}'")
    else:
        print(f"Error running VTC on '{str(file)}: {result.stderr}")

    return


def get_audio_files(recordings_dir: Path) -> Set[Path]:
    recording_formats: Set[str] = {r.value for r in RecordingFormats}
    audio_files: Set[Path] = set()

    for format in recording_formats:
        audio_files.update(recordings_dir.rglob(f"*.{format}"))

    return audio_files


def get_dataset_dir(dataset_dir: Path, dataset_id_label: str) -> Path:
    return dataset_dir / dataset_id_label


def get_task_output_dir(
    echolalia_dir: Path, task_id: UUID, dataset_id_label: str
) -> Path:
    return get_output_dir(echolalia_dir) / dataset_id_label / str(task_id)


def get_output_dir(echolalia_dir: Path) -> Path:
    return echolalia_dir / "outputs"
