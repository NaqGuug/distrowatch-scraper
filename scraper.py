from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timezone
import json
import os

# Constants
PARSER: str = "html5lib"
EXTRACT_DIRECTORY: str = os.getcwd() + "/data"
DISTOWATCH_URL: str = "https://distrowatch.com/"
URL_EXTENSION: str = "table.php?distribution="
REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla Gecko"
}
first_number: re.Pattern = re.compile(r"\d+")


def get_distros() -> list[str]:
    """Return list of all distros"""
    # Get DistroWatch main page
    main_page: str = requests.get(
        url=DISTOWATCH_URL,
        headers=REQUEST_HEADERS
    )
    soup: BeautifulSoup = BeautifulSoup(main_page.text, PARSER)

    # Get options from news page
    news_filtering: BeautifulSoup = soup.find(attrs={"class": "Introduction"})
    distro_select: BeautifulSoup = news_filtering.find("select", attrs={"name": "distribution"})
    # Get all distros
    distros: list[str] = []
    for options in distro_select.find_all("option"):
        if options.string == "All":
            # Default selection, not a distro
            continue
        distros.append(options.get("value"))

    return distros


def extract_distro_data(name: str, images: bool = True) -> None:
    """Extract distro data and save to files"""
    # Get distro page
    distro_page = requests.get(
        url=DISTOWATCH_URL+URL_EXTENSION+name,
        headers=REQUEST_HEADERS
    )
    distro_soup: BeautifulSoup = BeautifulSoup(distro_page.text, PARSER)
    info_page: BeautifulSoup = distro_soup.find(attrs={"class": "TablesTitle"})

    # Distro info saved to json
    distro_info: dict = {}
    distro_info["slug"] = name

    # Distro full name
    distro_info["name"] = info_page.h1.extract().text

    # Last update
    update_text: list[str] = info_page.h2.extract().text.split(" ")
    last_update: str = f"{update_text[2]}T{update_text[3]}:00Z"
    distro_info["lastUpdate"] = last_update

    # Info list (ul) [#1]
    distro_info_soup: BeautifulSoup = info_page.ul.extract()

    # Distro description [Save here for better ordering]
    distro_info["description"] = info_page.text.strip().partition("\n")[0]

    # Info list (ul) [#2]
    for li in distro_info_soup.find_all("li"):
        # Key
        key_part: tuple[str, str, str] = li.b.extract().text.partition(" ")
        key: str = f"{key_part[0].lower()}{key_part[2].capitalize()}"[:-1]

        # Value
        value: str = li.get_text().strip()

        distro_info[key] = value

    # Manual edits to status and popularity
    distro_info["status"] = distro_info["status"].partition(" ")[0]
    try:
        # Get popularity and hits per day
        popularity_partition: tuple[str, str, str] = distro_info["popularity"].partition(" ")
        distro_info["popularity"] = int(popularity_partition[0])
        distro_info["hitsPerDay"] = int(first_number.search(popularity_partition[2]).group())
    except ValueError:
        # Popularity not ranked
        distro_info["popularity"] = 0
        distro_info["hitsPerDay"] = 0

    # Rating
    bold_text = info_page.find_all("b")
    try:
        # Get rating and review count
        distro_info["rating"] = int(bold_text[-1].text)
        distro_info["reviewCount"] = float(bold_text[-2].text)
    except ValueError or KeyError:
        # Not rated
        distro_info["rating"] = 0
        distro_info["reviewCount"] = 0.0

    # Image urls
    distro_info["logo"] = DISTOWATCH_URL + info_page.find("img", attrs={"class": "logo"}).get("src")
    screenshot_a = info_page.a
    thumbnail_img = screenshot_a.img
    if thumbnail_img:
        distro_info["screenshot"] = DISTOWATCH_URL + screenshot_a.get("href")
        distro_info["thumbnail"] = DISTOWATCH_URL + thumbnail_img.get("src")
    else:
        distro_info["screenshot"] = None
        distro_info["thumbnail"] = None

    # Image local paths
    distro_info["localPaths"] = {
        "logo": f"{EXTRACT_DIRECTORY}/logos/{name}_logo.png" if distro_info["logo"] else None,
        "thumbnail": f"{EXTRACT_DIRECTORY}/thumbnails/{name}_thumbnail.png" if distro_info["thumbnail"] else None,
        "screenshot": f"{EXTRACT_DIRECTORY}/screenshots/{name}_screenshot.png" if distro_info["screenshot"] else None
    }

    # Extract images
    if images:
        # Fetch logo
        logo: bytes = requests.get(
            url=distro_info["logo"],
            headers=REQUEST_HEADERS
        ).content

        with open(distro_info["localPaths"]["logo"], "wb") as lf:
            lf.write(logo)

        # Fetch thumbnail
        if distro_info["thumbnail"]:
            thumbnail: bytes = requests.get(
                url=distro_info["thumbnail"],
                headers=REQUEST_HEADERS
            ).content

            with open(distro_info["localPaths"]["thumbnail"], "wb") as tf:
                tf.write(thumbnail)

        # Fetch screenshot
        if distro_info["screenshot"]:
            screenshot: bytes = requests.get(
                url=distro_info["screenshot"],
                headers=REQUEST_HEADERS
            ).content

            with open(distro_info["localPaths"]["screenshot"], "wb") as sf:
                sf.write(screenshot)

    # Extracted (current time)
    distro_info["extracted"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Save json
    with open(f"{name}.json", "w") as json_file:
        json.dump(distro_info, json_file)


def main() -> None:
    os.makedirs(EXTRACT_DIRECTORY, exist_ok=True)
    os.makedirs(EXTRACT_DIRECTORY + "/logos", exist_ok=True)
    os.makedirs(EXTRACT_DIRECTORY + "/thumbnails", exist_ok=True)
    os.makedirs(EXTRACT_DIRECTORY + "/screenshots", exist_ok=True)
    # distros = get_distros()
    # print(len(distros))
    extract_distro_data("gnuinos")
    # extract_distro_data("eagle")
    # extract_distro_data("qlustar")
    # extract_distro_data("kolibri")


if __name__ == "__main__":
    main()
