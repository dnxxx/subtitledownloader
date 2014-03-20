import logging
from datetime import datetime, timedelta
from time import sleep
import zipfile

from unipath import Path, FILES
from lazy import lazy

from .subscene import Subscene


log = logging.getLogger(__name__)
SLEEP_TIME = 30


class SubtitleDownloaderError(Exception):
    pass


class SubtitleDownloader(object):
    def __init__(self, search_dir, search_all=False):
        self.search_dir = Path(search_dir)
        self.search_all = search_all

        # Make sure the sort dir is a dir and cd into it
        if not self.search_dir.isdir():
            raise SubtitleDownloaderError('Invalid search-dir {}'.format(
                search_dir))

    @staticmethod
    def relative_path(path, root_path):
        """Return the relative path of path in root_path"""

        relative_path = path.replace(root_path, '')
        if relative_path[0:1] == '/':
            return relative_path[1:]
        else:
            return relative_path

    def scan_for_search_files(self):
        """Scan search dir and return all files to search subtiles for"""

        log.debug('Searching for files in dir {}'.format(self.search_dir))

        search_files = []
        for file_path in self.search_dir.walk(filter=FILES, top_down=False):
            if not file_path.ext in ('.mkv', '.avi'):
                continue

            subtitle_download = SubtitleDownload(file_path)

            # Search for subtitle if self.search_all is True or if the file
            # modified time is in the last week
            search_subtitle = self.search_all or \
                subtitle_download.time_since_modified < timedelta(weeks=1)

            # Don't search subtitle for this file
            if not search_subtitle:
                continue

            # Check if subtitle already exists
            if subtitle_download.subtitle_exist():
                log.debug('Subtitle for {} already exists'.format(
                    self.relative_path(file_path, self.search_dir)))
                continue

            search_files.append(subtitle_download)

        return search_files

    def scan_search(self):
        """Scan for files to download subtitles for and try to download
        subtitle.
        """

        search_files = self.scan_for_search_files()
        num_searches = len(search_files)
        for i, subtitle_download in enumerate(search_files):
            log.info('Subtitle search for {}'.format(subtitle_download.name))

            subtitle_download.search_download_subtitle()

            # Sleep between searches if it's not the last search file
            if i + 1 != num_searches:
                log.info('Sleeping for {} seconds'.format(SLEEP_TIME))
                sleep(SLEEP_TIME)

    def cleanup(self):
        """Remove subtitle files left over where the media file is removed"""

        log.debug('Running subtitle cleanup on dir {}'.format(self.search_dir))

        subtitle_extensions = ('.srt', '.sub', '.idx')

        for file_path in self.search_dir.walk(filter=FILES, top_down=False):
            if not file_path.ext in subtitle_extensions:
                continue

            # Remove the subtitle file if no media file exists in the same dir
            media_file_path_mkv = Path(file_path.parent, '{}.mkv'.format(
                file_path.stem))
            media_file_path_avi = Path(file_path.parent, '{}.avi'.format(
                file_path.stem))
            if (not media_file_path_mkv.exists() and
                    not media_file_path_avi.exists()):
                log.info('Removing leftover subtitle file {}'.format(
                    self.relative_path(file_path, self.search_dir)))

                file_path.remove()


class SubtitleDownload(object):
    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.stem
        self.download_dir = self.path.parent

    def __unicode__(self):
        return self.name

    @lazy
    def time_since_modified(self):
        mtime_datetime = datetime.fromtimestamp(self.path.mtime())
        return datetime.now() - mtime_datetime

    def subtitle_exist(self):
        if (Path(self.download_dir, '{}.srt'.format(self.name)).exists() or
                Path(self.download_dir, '{}.sub'.format(self.name)).exists()):
            return True
        else:
            return False

    def search_download_subtitle(self):
        """Search subtitle services and download subtitle"""

        subscene_downloaded_zip = self.subscene_download()
        if subscene_downloaded_zip:
            self.process_zip(subscene_downloaded_zip)

    def subscene_download(self):
        subscene = Subscene(self.name)

        if not subscene.search_match():
            log.info('No Subscene match for {}'.format(self.name))
            return False

        return subscene.download_zip(self.download_dir)

    def process_zip(self, zip_file_path):
        """Process the subtitle zip and extract all files with a valid file
        extension. Remove the zip file when done.
        """

        # Make sure the downloaded zip file is valid
        if not zipfile.is_zipfile(zip_file_path):
            log.info('Invalid zip file {}'.format(
                SubtitleDownloader.relative_path(zip_file_path,
                                                 self.download_dir)))
            zip_file_path.remove()
            return False

        zip_file = zipfile.ZipFile(zip_file_path)
        for file in zip_file.namelist():
            file = Path(file)

            # Check file extension
            if not file.ext.lower() in ('.srt'):
                log.debug('Invalid subtitle file extension {}, '
                          'skipping'.format(file))
                continue

            # Name of unpacked subtitle file and the renamed subtitle file
            unpacked_subtitle_file = Path(self.download_dir, file)
            renamed_subtitle_file = Path(self.download_dir, '{}{}'.format(
                self.name, unpacked_subtitle_file.ext.lower()))

            # Skip the subtitle file if it's already exists
            if renamed_subtitle_file.exists():
                log.info('{} already exists'.format(
                    SubtitleDownloader.relative_path(renamed_subtitle_file,
                                                     self.download_dir)))
                continue

            # Extract the file to unpack dir and then move it to match the name
            # of the subtitle search
            log.info('Found subtitle, extracting subtitle file {}'.format(
                SubtitleDownloader.relative_path(renamed_subtitle_file,
                                                 self.download_dir)))
            zip_file.extract(file, self.download_dir)
            unpacked_subtitle_file.move(renamed_subtitle_file)

        # Remove the zip file
        zip_file_path.remove()
