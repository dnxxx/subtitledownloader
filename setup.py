from distutils.core import setup

import subtitledownloader

setup(
    name='subtitledownloader',
    version=subtitledownloader.__version__,
    description='Subtitle downloader',

    packages=['subtitledownloader'],
    scripts=['bin/subtitledownloader'],

    author='dnxxx',
    author_email='dnx@fbi-security.net',
    license='BSD',

    install_requires=[
        'unipath',
        'argh',
        'requests',
        'beautifulsoup4',
        'lazy',
    ]
)
