from pathlib import Path

import click
from ChildProject.annotations import AnnotationManager
from ChildProject.pipelines.zooniverse import ZooniversePipeline
from ChildProject.projects import ChildProject


@click.command()
@click.option(
    "--dataset-path",
    type=click.Path(exists=True),
    help="Path to ChildProject dataset root",
)
@click.option(
    "--segments-path",
    type=click.Path(exists=True),
    help="Path to segments .csv",
)
@click.option(
    "--destination-path",
    type=click.Path(),
    help="Path to destination folder",
)
@click.option(
    "--threads",
    type=int,
    default=16,
    help="Number of threads",
)
def do_importation(
    dataset_path: Path, segments_path: Path, destination_path: Path, threads: int
) -> None:
    """
    Creates chunks through a ChildProject importation
    """
    project = ChildProject(dataset_path)
    project.read()
    am = AnnotationManager(project)
    am.read()

    zooniverse = ZooniversePipeline()

    zooniverse.extract_chunks(
        path=project.path,
        destination=destination_path,
        keyword="maturity",
        segments=segments_path,
        chunks_length=500,
        spectrogram=False,
        profile="standard",
        threads=int(threads),
        chunks_min_amount=1,
    )

    return


if __name__ == "__main__":
    do_importation()
