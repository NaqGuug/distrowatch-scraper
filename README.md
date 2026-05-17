# DistroWatch Scraper
Python script for scraping information of all distributions from [DistroWatch](https://distrowatch.com/) database.

## Description

This program is designed to scrape distrobution data from DistroWatch, as currently
DistroWatch doesn't provide an easy way to download this data. If you are
interested in data analytics, statistics and OS distrobutions, this program is for you.

The program will search available distrobutions from news section's distribution tab in main page.
This tab includes distros which are not normally visible in distrobution search.
With distrobution names in hand the program will visit each distro page and scrape available
data, including images. The data will be stored to a json file and images to separate folders.

## Getting Started

### Dependencies

- python
- pip
- git (optional)

### Installing

Clone the repo

```console
git clone https://github.com/NaqGuug/distrowatch-scraper.git
```

Create virtual environment and activate it

```console
python -m venv .venv/
source .venv/bin/activate
```

Install dependencies with pip

```console
pip install -r requirements.txt
```

### Executing program

Scrape distro information.

```console
python distroscraper.py
```

Scrape distro information and download images.

```console
python distroscraper.py -i
```

By default the program won't scrape already scraped distros.
To scrape everything and override old files, run the program with `-f` flag.

```console
python distroscraper.py -i -f
```

## Output Structure

The output structure follows heavily [felagund1789's Scraper](https://github.com/felagund1789/distrowatch-scraper)
with few modifications
```
data/
├── distros.json                    # Complete distribution data
└── images/
    ├── logos/                      # Distribution logos
    │   ├── ubuntu-logo.png
    │   ├── fedora-logo.png
    │   └── ...
    ├── thumbnails/                 # Small screenshot thumbnails
    │   ├── ubuntu-thumbnail.png
    │   ├── fedora-thumbnail.png
    │   └── ...
    └── screenshots/                # High-resolution screenshots
        ├── ubuntu-screenshot.png
        ├── fedora-screenshot.png
        └── ...
```

## Help

```console
usage: distroscraper.py [-h] [-o OUTPUT] [-f] [-i] [-l] [-t] [-s]

Scrape distro information and images from DistroWatch.com

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Output directory
  -f, --force-update   Force update existing data
  -i, --images         Scrape all images
  -l, --logos          Scrape logos
  -t, --thumbnails     Scrape thumbnails
  -s, --screenshots    Scrape screenshots
```

## See Also
- [DistroWatch](https://distrowatch.com/)
- [felagund1789's Scraper](https://github.com/felagund1789/distrowatch-scraper) - Node.js application for scraping DistroWatch
- [sxiii's Scraper](https://github.com/sxiii/distrowatch-scraper/) - DistroWatch scraper written in bash
