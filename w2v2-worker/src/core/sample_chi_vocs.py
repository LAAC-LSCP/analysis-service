from pathlib import Path

import click
from ChildProject.annotations import AnnotationManager
from ChildProject.projects import ChildProject


@click.command()
@click.option(
    "--dataset-path",
    type=click.Path(exists=True),
    help="Path to ChildProject dataset root",
)
@click.option(
    "--output-path",
    type=click.Path(exists=False),
    help="Path to output .csv file",
)
def sample_chi_vocs(dataset_path: str, output_path: str):
    project = ChildProject(dataset_path)
    project.read()
    am = AnnotationManager(project)
    am.read()

    vtc = am.annotations[am.annotations["set"] == "vtc"]
    segments = am.get_segments(vtc)

    kchi_segments = segments[segments["speaker_type"] == "CHI"]
    kchi_segments[["recording_filename", "segment_onset", "segment_offset"]].to_csv(
        Path(output_path), index=False
    )

    return


if __name__ == "__main__":
    sample_chi_vocs()
