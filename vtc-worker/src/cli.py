import json
import os
from pathlib import Path

import click
import redis

from src.core.channels import ChannelName, CompleteTask, RunTask
from src.core.config import Config
from src.core.redis_utils import get_redis_host_and_port
from src.core.run_vtc import run_vtc as run_vtc_cmd


@click.command()
def run_vtc():
    """
    Run VTC worker with the specified task ID.
    """
    r = redis.Redis(**get_redis_host_and_port())

    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(ChannelName.RUN_VTC)

    config = get_config()

    print("Starting vtc...")
    for message in pubsub.listen():
        print(f"Listening in on channel '{ChannelName.RUN_VTC}'")
        data: dict = json.loads(message["data"].decode("utf-8"))

        run_task = RunTask.from_dict(dict_repr=data)

        if not (config.datasets_dir / run_task.dataset_uid_label).exists():
            raise ValueError(
                f"Dataset '{run_task.dataset_uid_label}' not found in \
'{config.datasets_dir}'"
            )

        run_vtc_cmd(run_task.task_id, run_task.dataset_uid_label, config)

        print("VTC ran successfully. Publishing to redis...")
        r.publish(
            ChannelName.COMPLETE_TASK,
            json.dumps(CompleteTask(task_id=run_task.task_id).to_dict()),
        )

    return


def get_config() -> Config:
    echolalia_dir = load_path("ECHOLALIA_DIR")
    datasets_dir = load_path("DATASETS_DIR")
    conda_activate_file = load_path("CONDA_ACTIVATE_FILE")
    conda_env_name = load_str("CONDA_ENV_NAME")

    return Config(
        echolalia_dir=echolalia_dir,
        datasets_dir=datasets_dir,
        conda_activate_file=conda_activate_file,
        conda_env_name=conda_env_name,
    )


def load_str(env_var: str) -> str:
    string: str | None = os.environ.get(env_var, None)

    if string is None:
        raise ValueError(f"'{env_var} env variables not set")

    return string


def load_path(env_var: str) -> Path:
    dir_as_str: str | None = os.environ.get(env_var, None)

    if dir_as_str is None:
        raise ValueError(f"'{env_var}' env variable not set")

    dir = Path(dir_as_str)
    if not dir.exists():
        raise FileNotFoundError(f"File at '{str(dir)}' not found")

    return dir


if __name__ == "__main__":
    run_vtc()
