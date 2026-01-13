import shutil
import subprocess
from pathlib import Path

from analysis_service_core.src.model import ModelPlugin


class VTC_2(ModelPlugin):
    def run_model(self, dataset_dir: Path, output_dir: Path) -> None:
        recordings_path = dataset_dir / "recordings" / "converted"
        self._do_vtc(recordings_path, output_dir)

        return

    def _do_vtc(self, input: Path, output: Path) -> None:
        sub_dirs = [dir for dir in input.iterdir() if dir.is_dir()]
        files = [f for f in input.iterdir() if f.is_file()]

        if len(files):
            self._call_vtc(input, output)
            self._move_and_clean(output)

        for dir in sub_dirs:
            self._do_vtc(dir, output / dir.name)

        return

    def _move_and_clean(self, dir: Path) -> None:
        raw_rttm_dir = dir / "raw_rttm"
        shutil.rmtree(raw_rttm_dir)

        for csv_name in ["raw_rttm.csv", "rttm.csv"]:
            csv_path = dir / csv_name
            csv_path.unlink()

        rttm_dir = dir / "rttm"
        for item in rttm_dir.iterdir():
            shutil.move(str(item), str(dir / item.name))

        rttm_dir.rmdir()

        return

    def _call_vtc(self, input: Path, output: Path) -> None:
        vtc_folder = self.config.get("VTC_2_FOLDER")
        device = self.config.get("VTC_2_DEVICE")
        bash_script = f"""
        uv run scripts/infer.py --wavs {str(input)} --output {str(output)} \
--device={device}
        """

        self._run_subprocess(bash_script, vtc_folder, input)

        return

    def _run_subprocess(self, bash_script: str, cwd: Path, input_dir: Path) -> None:
        # Note that vtc 2 has a quirk that it puts outputs in the current working dir
        result = subprocess.run(
            ["bash", "-c", bash_script], cwd=cwd, capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"Successfully ran VTC on folder '{str(input_dir)}'")
        else:
            print(f"Error running VTC on folder '{str(input_dir)}: {result.stderr}")

        return
