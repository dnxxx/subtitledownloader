import re

import requests
from bs4 import BeautifulSoup
from unipath import Path


class Subscene(object):
    def __init__(self, search):
        self.search = search
        self.re = re.compile(self.search, re.I)

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/32.0.1700.107 Safari/537.36'}

    def search_match(self):
        """Search and find a match for subtitle. Returns True if a subtitle
        match was found.
        """

        # Fetch the search page
        req = requests.get(('http://subscene.com/subtitles/'
                           'release?q={}').format(self.search),
                           headers=self.headers)

        # Try to find a match on search page
        soup = BeautifulSoup(req.text)
        for result in soup.select('table tr td.a1'):
            url = result.select('a')[0].attrs['href']
            lang = result.select('span')[0].text.strip()
            name = result.select('span')[1].text.strip()

            # A match is found
            if lang == 'English' and self.re.search(name):
                self.download_page_url = url
                return True

        return False

    def download_zip(self, download_dir):
        """Download the matched subtitle to download_dir. Returns the path to
        the downloaded zip file."""

        # Fetch the download page to get the download url for the zip file
        req = requests.get('http://subscene.com{}'.format(
            self.download_page_url), headers=self.headers)
        soup = BeautifulSoup(req.text)
        download_url = soup.select('.download a')[0].attrs['href']

        # Download the subtitle zipfile
        zip_file_path = Path(download_dir, '{}.zip'.format(self.search))
        with open(zip_file_path, 'wb') as handle:
            req = requests.get('http://subscene.com{}'.format(download_url),
                               headers=self.headers)

            for block in req.iter_content(1024):
                if not block:
                    break

                handle.write(block)

        return zip_file_path
