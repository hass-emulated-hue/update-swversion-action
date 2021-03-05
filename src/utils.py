import json
import logging
import os
import shutil
from tempfile import mkstemp

LOGGER = logging.getLogger(__name__)


def load_json(filename: str) -> dict:
    """Load JSON from file."""
    try:
        with open(filename, encoding="utf-8") as fdesc:
            return json.loads(fdesc.read())
    except (FileNotFoundError, ValueError, OSError) as error:
        LOGGER.exception("Loading %s failed: %s", filename, error)
        exit(1)


def save_version_in_file(filename: str, current_version: str, new_version: str) -> None:
    """Search and replace value in file."""
    # This works by creating a temporary file, reading and replacing the
    try:
        fd, temp_path = mkstemp()
        with open(fd, 'w') as temp_file:
            with open(filename) as old_file:
                for line in old_file:
                    if current_version in line and '"swversion": "' in line:
                        new_line = line.replace(current_version, new_version)
                    else:
                        new_line = line
                    temp_file.write(new_line)
        shutil.copy(temp_path, filename)
        os.remove(temp_path)
    except IOError:
        LOGGER.exception("Failed replacing version number: %s", filename)
        exit(1)


def test_cast_int(potential_int: str) -> bool:
    """Test if string can be casted to int."""
    # Attempt to cast to int to ensure we have a version number
    # Return string since some versions begin with 0
    try:
        int(potential_int)
        return True
    except ValueError:
        return False
