"""Ran daily to automatically obtain and commit latest swversion."""

import logging
import os
import re
from typing import Optional

import requests

from utils import load_json, save_version_in_file, test_cast_int

logger = logging.getLogger()
logformat = logging.Formatter(
    "%(asctime)-15s %(levelname)-5s %(name)s -- %(message)s")
consolehandler = logging.StreamHandler()
consolehandler.setFormatter(logformat)
logger.addHandler(consolehandler)
logger.setLevel(logging.INFO)
LOGGER = logging.getLogger("Updater")


def extract_version(line) -> Optional[str]:
    """Parse line from webpage and return version number."""
    # Check to see if match the standard firmware version 1/2
    match = re.search(r"(version)(.{0,3}?)([0-9.]+)", line)
    if match:
        version_str = match.group(3)
        return version_str if test_cast_int(version_str) else None


def get_latest_version() -> str:
    """Scrape latest Hue version from website."""
    url = "https://www.philips-hue.com/en-us/support/release-notes/bridge"
    response = requests.get(url)
    webpage_lines = []
    for x in response.content.decode("utf-8").splitlines():
        if x:
            webpage_lines.append(re.sub(r"[^A-Za-z0-9 .]+", "", x.lower()))
    # Find first version number on page
    for line in webpage_lines:
        version = extract_version(line)
        if version:
            return version


if __name__ == "__main__":
    if os.getenv("GITHUB_WORKSPACE"):
        DEFINITIONS_FILE = os.path.join(
            os.getenv("GITHUB_WORKSPACE", ""), "emulated_hue/definitions.json"
        )
        definitions = load_json(DEFINITIONS_FILE)

        latest_version = get_latest_version()

        current_version = definitions["bridge"]["basic"]["swversion"]
        LOGGER.info("Current version: %s, Latest version: %s",
                    current_version, latest_version)

        if current_version != latest_version:
            LOGGER.info(
                "Current version is not equal to latest version! Writing latest version: %s", latest_version
            )
            definitions["bridge"]["basic"]["swversion"] = latest_version
            save_version_in_file(
                DEFINITIONS_FILE, current_version, latest_version)
        else:
            LOGGER.info(
                "Current version is equal to latest version. Exiting...")
        os.system(f'echo ::set-output name=version::{latest_version}')
    else:
        # For testing when not in GitHub Actions
        print(f"Latest version is {get_latest_version()}")
