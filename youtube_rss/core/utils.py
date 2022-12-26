from typing import Any

from pathlib import Path

import yaml


def import_yaml(file_path: str | Path) -> dict[str, Any]:
    with open(file=file_path, mode="r", encoding="utf-8") as stream:
        try:
            return yaml.safe_load(stream=stream)
        except yaml.YAMLError as e:
            raise e
