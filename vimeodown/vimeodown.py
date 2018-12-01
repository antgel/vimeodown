#!/usr/bin/env python

import argparse
import logging
import os
import re
import sys

import requests
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


next = f"/users/{args.username}/videos"
save_dir = f"{args.mountpoint}/vimeodown"

try:
    os.mkdir(save_dir)
except FileExistsError:
    pass

while next:
    r = v.get(next)
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
        logger.info(f"Attempting: {filename}")
        save_path = f"{save_dir}/{filename}"
        logger.debug(f"Save path: {save_path}")

        # If the file already exists, move on.
        if os.path.isfile(save_path):
            logger.info(f"{save_path} exists at destination, skipping")
            continue

        r = requests.get(download_url, allow_redirects=True)
        open(save_path, 'wb').write(r.content)

    next = r_j['paging']['next']
    logger.debug(f"Next page: {next}")
