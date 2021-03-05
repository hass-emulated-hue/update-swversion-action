"""Ran daily to automatically obtain and commit latest swversion."""

import logging
import os
import re
from typing import Optional

import requests

from utils import load_json, save_json, test_cast_int

logger = logging.getLogger()
logformat = logging.Formatter("%(asctime)-15s %(levelname)-5s %(name)s -- %(message)s")
consolehandler = logging.StreamHandler()
consolehandler.setFormatter(logformat)
logger.addHandler(consolehandler)
logger.setLevel(logging.INFO)
LOGGER = logging.getLogger("Updater")

get_match_string = lambda match_result: ''.join(match_result.groups())


def extract_version(line) -> Optional[str]:
    """Parse line from webpage and return version number."""
    # Check to see if match the standard firmware version 1/2
    match = re.search("(firmware)(.*)([0-9]+)(.*)(v2)(.*)([0-9]*)", line)
    if match:
        partial = get_match_string(match)
        # Looks like (characters)v2(characters)(version)
        format_1 = re.search(r"(v2)(.*?)([0-9]+)", partial)
        if format_1:
            version_str = format_1.group(3)
        else:
            # Looks like (version)(characters)(v2)
            format_2 = re.search(r"([0-9]+)(.*?)(v2)", partial)
            version_str = format_2.group(1)
        return version_str if test_cast_int(version_str) else None
    else:
        # Check if matches firmware (int) without v1
        match = re.search("(firmware)(.*?)([0-9]+)", line)
        v1_match = re.search("(v1)", line)
        if not v1_match and match:
            version_str = match.group(3)
            return version_str if test_cast_int(version_str) else None


def get_latest_version() -> str:
    """Scrape latest Hue version from website."""
    url = "https://www.philips-hue.com/en-us/support/release-notes/bridge"
    response = requests.get(url)
    webpage_lines = []
    for x in response.content.decode("utf-8").splitlines():
        if x:
            webpage_lines.append(re.sub(r"[^A-Za-z0-9 ]+", "", x.lower()))
    versions = list(filter(None, map(extract_version, webpage_lines)))
    # assume versions are in listed in order from newest to oldest. Next best alternative to saving all dates
    return versions[0]


DEFINITIONS_FILE = os.path.join(
    os.getenv("GITHUB_WORKSPACE", ""), "emulated_hue/definitions.json"
)
definitions = load_json(DEFINITIONS_FILE)

latest_version = get_latest_version()

current_version = definitions["bridge"]["basic"]["swversion"]
LOGGER.info(f"Current version: {current_version}, Latest version: {latest_version}")

if current_version != latest_version:
    LOGGER.info(
        f"Current version is not equal to latest version! Writing latest version: {latest_version}"
    )
    definitions["bridge"]["basic"]["swversion"] = latest_version
    save_json(DEFINITIONS_FILE, definitions, False)
else:
    LOGGER.info(f"Current version is equal to latest version. Exiting...")
os.system(f'echo ::set-output name=version::{latest_version}')
