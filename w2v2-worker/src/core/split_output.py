#!usr/bin/env python
# -*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   splits the output of the w2v2-sm model into recording level
# -----------------------------------------------------------------------------
from pathlib import Path

import click
import pandas as pd
from ChildProject.projects import ChildProject

MAP_VCM = {
    "Canonical": "C",
    "Non-Canonical": "N",
    "Junk": "J",
    "Crying": "Y",
    "Laughing": "L",
}


@click.command()
@click.option(
    "--dataset-path",
    type=click.Path(exists=True),
    help="Path to ChildProject dataset root",
)
@click.option(
    "--w2v2-predictions-csv",
    type=click.Path(exists=False),
    help="Path to output .csv file",
)
@click.option(
    "--output-path",
    type=click.Path(exists=False),
    help="Path to output folder",
)
def split_output(dataset_path: str, w2v2_predictions_csv: str, output_path: str):
    csv = Path(w2v2_predictions_csv)
    output_folder = Path(output_path)

    try:
        if output_folder.exists():
            output_folder.rmdir()
        output_folder.mkdir(parents=True, exist_ok=True)
    except Exception:
        exit(1)

    df = pd.read_csv(csv)
    df["recording_filename"] = df["id"].apply(
        lambda x: "_".join(x.split("_")[:-2]) + ".wav"
    )  # assuming lowercase wav and no subfolder
    df["segment_onset"] = df["id"].apply(lambda x: int(x.split("_")[-2]))
    df["segment_offset"] = df["id"].apply(lambda x: int(x.split("_")[-1]))

    for rec, gdf in df.groupby("recording_filename"):
        gdf["vcm_type"] = gdf["prediction_class_name"].map(MAP_VCM)
        to_save = gdf[
            ["recording_filename", "segment_onset", "segment_offset", "vcm_type"]
        ]

        output = (output_folder / rec).with_suffix(".csv")
        output.parent.mkdir(exist_ok=True)
        to_save.to_csv(output, index=False)

    dataset = ChildProject(Path(dataset_path))
    dataset.read()
    existing_filenames = df["recording_filename"].unique()
    for rec in dataset.recordings["recording_filename"].unique():
        if rec not in existing_filenames:
            output = (output_folder / rec).with_suffix(".csv")
            output.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(
                [],
                columns=[
                    "recording_filename",
                    "segment_onset",
                    "segment_offset",
                    "vcm_type",
                ],
            ).to_csv(output, index=False)


if __name__ == "__main__":
    split_output()
