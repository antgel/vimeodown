#!/usr/bin/env python

import argparse
import logging
import os
import re
import sys
import time

import requests
from urllib3.exceptions import MaxRetryError
import vimeo


parser = argparse.ArgumentParser()
parser.add_argument("username", help="Your Vimeo username")
parser.add_argument("mountpoint",
                    help="Full path to destination directory")
args = parser.parse_args()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

logger.addHandler(ch)

if ("VIMEO_TOKEN" not in os.environ
        or "VIMEO_KEY" not in os.environ
        or "VIMEO_SECRET" not in os.environ):
        logger.error('''Please set environment variables VIMEO_TOKEN,
                     VIMEO_KEY, VIMEO_SECRET''')
        sys.exit(1)

v = vimeo.VimeoClient(
    token=os.environ['VIMEO_TOKEN'],
    key=os.environ['VIMEO_KEY'],
    secret=os.environ['VIMEO_SECRET']
)


# Thanks to https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un
def get_filename_from_cd(cd):
    """
    Get filename from content-disposition header
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


def get_with_retry(url):
    # Why don't we do this properly e.g. as per
    # https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    # Because vimeo.py already wraps `requests` and things get complex.
    try:
        return v.get(url, allow_redirects=True)
    except (requests.Timeout, MaxRetryError):
        seconds_to_wait = 1
        time.sleep(seconds_to_wait)
        logger.info('Connection issue, retrying')
        return get_with_retry(url)


next_url = f"/users/{args.username}/videos"
save_dir = f"{args.mountpoint}/vimeodown"

try:
    os.mkdir(save_dir)
except FileExistsError:
    pass

while next_url:
    logger.debug(f"Getting video list from {next_url}")
    r = get_with_retry(next_url)
    assert r.status_code == 200
    r_j = r.json()
    for video in r_j['data']:
        download_url = video['download'][0]['link']
        r = requests.head(download_url, allow_redirects=True)
        filename = get_filename_from_cd(r.headers.get('content-disposition'))
        # Chop the start and end quotes from the filename
        filename = filename[1:-1]
        # Remove special characters as they don't work in filenames
        # FIXME: Maybe escaping them would been better, but who cares?
        filename = filename.replace(':', '')
        filename = filename.replace('/', '')
        filename = filename.replace('|', '')
        save_path = f"{save_dir}/{filename}"

        logger.debug(f"Checking {filename}")
        # If the file already exists, move on.
        if os.path.isfile(save_path):
            logger.debug(f"Skipping {filename}, exists at destination")
            continue

        logger.info(f"Downloading {filename}")
        r = get_with_retry(download_url)
        logger.info(f"Saving to {save_path}")
        open(save_path, 'wb').write(r.content)

    next_url = r_j['paging']['next']
