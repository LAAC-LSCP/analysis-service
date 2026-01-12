"""
After some work I got VTC to run on a VM I provisioned
But it requires fairly specific hardware to work

I mock the input/output behaviour of VTC below
"""

import shutil
from pathlib import Path

from src.core.vtc_2 import VTC_2


class VTC_2_Mock(VTC_2):
    def _call_vtc(self, input: Path, output: Path) -> None:
        """
        Mimicks calling VTC roughly as follows:
        `uv run scripts/infer.py --wavs [input] --output [output]`

        The behaviour of VTC_2 is such that:
        if you pass in a folder with some .wav files it gives you:
        - raw_rttm/ folder
            - inside a list of .rttm files with the same filenames as inputs
        - raw_rttm.csv
        - rttm/ folder
            - inside a list of .rttm files with the same filenames as inputs
        - rttm.csv

        It does NOT recurse into subfolders
        """
        files = [f for f in input.iterdir() if f.is_file()]

        if len(files) == 0:
            return

        (output / "raw_rttm").mkdir(parents=True, exist_ok=True)
        (output / "rttm").mkdir(parents=True, exist_ok=True)

        for f in files:
            shutil.copy(f, output / "raw_rttm" / (f.stem + ".rttm"))
            shutil.copy(f, output / "rttm" / (f.stem + ".rttm"))
            (output / "raw_rttm.csv").touch(exist_ok=True)
            (output / "rttm.csv").touch(exist_ok=True)

        return
