import tomllib
from pathlib import Path

from analysis_service_core.src.logger import LoggerFactory
from pydantic import BaseModel, Field, HttpUrl, ValidationError

logger = LoggerFactory.get_logger(__name__)


class HTTPConfig(BaseModel):
    base_url: HttpUrl = Field(description="Base URL of the site")
    client_id: str = Field(description="Client ID")
    client_secret: str = Field(description="Secret access key (do NOT share)")


class ConfigModel(BaseModel):
    http: HTTPConfig


def load_config(file_path: Path) -> ConfigModel:
    """
    loads the config for the service from a toml file
    Args:
        file_path: path of the toml config file
    Returns: a config object
    """
    with open(file_path, "rb") as f:
        raw = tomllib.load(f)

    try:
        return ConfigModel.model_validate(raw)
    except ValidationError as e:
        logger.err(f"Invalid configuration: {e}")
        raise
