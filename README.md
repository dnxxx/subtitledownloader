## Subtitle downloader
Find all media files (mkv, avi) and search for subtitles if no subtitle exists
already. An english subtitles will be downloaded from Subscene if a match
could be found. When downloaded the subtitle will be extracted and renamed to
match the media file. By default only media files modified in the last week
will be searched if -a isn't activated.

## Usage
    subtitledownloader /path/to/dir
    subtitledownloader --search-all /path/to/dir

## Help
    usage: subtitledownloader [-h] [-a] [-c] [-d] [-s] [-l LOG] [-v] search-dir

    Find all media files (mkv, avi) and search for subtitles if no subtitle exists
    already. An english subtitles will be downloaded from Subscene if a match
    could be found. When downloaded the subtitle will be extracted and renamed to
    match the media file. By default only media files modified in the last week
    will be searched if -a isn't activated.

    positional arguments:
      search-dir

    optional arguments:
      -h, --help         show this help message and exit
      -a, --search-all   Search all files (default: False)
      -c, --cleanup      Remove leftover subs files (default: False)
      -d, --debug        Output debug info (default: False)
      -s, --silent       Disable console output (default: False)
      -l LOG, --log LOG  Log to file (default: None)
      -v, --version      show program's version number and exit (default: False)

## Crontab example
    subtitledownloader --silent --log /path/to/log/dir/subtitledownloader.log /path/to/dir

## Install
    pip install git+https://github.com/dnxxx/subtitledownloader

## Warning
This hasn't been really battle tested yet, there will probably be bugs.

If cleanup is active all subtitle files without a matching media file will be
removed.

You've been warned!
