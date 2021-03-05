import os
import json
import logging

LOGGER = logging.getLogger(__name__)


def load_json(filename: str) -> dict:
    """Load JSON from file."""
    try:
        with open(filename, encoding="utf-8") as fdesc:
            return json.loads(fdesc.read())  # type: ignore
    except (FileNotFoundError, ValueError, OSError) as error:
        LOGGER.debug("Loading %s failed: %s", filename, error)
        return {}


def save_json(filename: str, data: dict, backup: bool = True):
    """Save JSON data to a file."""
    if backup:
        safe_copy = filename + ".backup"
        if os.path.isfile(filename):
            os.replace(filename, safe_copy)
    try:
        json_data = json.dumps(data, sort_keys=False, indent=2, ensure_ascii=False)
        with open(filename, "w") as file_obj:
            file_obj.write(json_data)
    except IOError:
        LOGGER.exception("Failed to serialize to JSON: %s", filename)


def test_cast_int(potential_int: str) -> bool:
    """Test if string can be casted to int."""
    # Attempt to cast to int to ensure we have a version number
    # Return string since some versions begin with 0
    try:
        int(potential_int)
        return True
    except ValueError:
        return False
