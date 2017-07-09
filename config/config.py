import json
import os
from typing import Dict, Any

_FILENAME = os.path.join(os.getcwd(), 'config', "config.json")


def load_config_value(key: str) -> str:
    try:
        config = _load_config()
    except FileNotFoundError:
        _create_config_file({'gmapsApiKey': ''})
        raise KeyError("Config value not found for " + key)
    except json.decoder.JSONDecodeError:
        raise KeyError("Config value not found for " + key)

    return config[key]


def _load_config() -> Dict[str, Any]:
    try:
        file = open(_FILENAME)
        config_data = json.load(file)
        file.close()
        return config_data
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        raise


def _create_config_file(structure: Dict):
    try:
        outfile = open(_FILENAME, 'w')
        json.dump(structure, outfile, indent=2)
        outfile.close()
    except IOError:
        raise
