# vimeodown

`vimeodown.py` is a simple script that downloads your Vimeo
videos to a local directory.

## Installation

* Install Python 3.
* Clone this repository and `cd` into the directory.
* `pip3 install -r requirements.txt`.

## Usage

* Set environment variables `VIMEO_TOKEN`, `VIMEO_KEY`, `VIMEO_SECRET`
to appropriate values.
* `vimeodown.py $username $mountpoint` where:
    * `$username` is your Vimeo username (you can get this by going to
    your Vimeo account homepage, something like
    https://vimeo.com/myusername).
    * `$mountpoint` is the directory where you want to save the files
    to. For an external hard disk, this will be something like
    `/media/someuser/mydisk` on Linux or `/Volumes/mydisk` for Mac.

## Miscellaneous

* The script won't attempt to redownload videos found at the
destination.
* The network error handling is agricultural and will retry forever in
the absence of a positive outcome.

## Disclaimer

This code was written for a specific purpose, and no warranty is given
or implied. Error handling is minimal, and bugs may luck.
