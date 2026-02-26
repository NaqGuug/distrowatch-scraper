from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime, timezone
import json

# Constants
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
    soup: BeautifulSoup = BeautifulSoup(main_page.text, "html.parser")

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


def extract_distro_data(name: str) -> None:
    """Extract distro data and save to files"""
    # Get distro page
    distro_page = requests.get(
        url=DISTOWATCH_URL+URL_EXTENSION+name,
        headers=REQUEST_HEADERS
    )
    distro_soup: BeautifulSoup = BeautifulSoup(distro_page.text, "html.parser")
    info_page: BeautifulSoup = distro_soup.find(attrs={"class": "TablesTitle"})

    # Distro info saved to json
    distro_info: dict[str, str | int | float] = {}
    distro_info["slug"] = name

    # Distro full name
    distro_info["name"] = info_page.h1.extract().text

    # Last update
    # TODO: convert to utc time format
    distro_info["lastUpdate"] = info_page.h2.extract().text

    # Info list (ul)
    distro_info_soup: BeautifulSoup = info_page.ul.extract()
    for li in distro_info_soup.find_all("li"):
        # Key
        key_part: tuple[str, str, str] = li.b.text.partition(" ")
        key: str = f"{key_part[0].lower()}{key_part[2].capitalize()}"[:-1]

        # Value
        links = li.find_all(["a", "font"], recursive=False)
        value: str = ", ".join([link.text for link in links])

        distro_info[key] = value

    # Manual edits to status and popularity
    distro_info["status"] = distro_info["status"].partition(",")[0]
    if not distro_info["popularity"]:
        # Popularity not ranked
        distro_info["popularity"] = 0
        distro_info["hitsPerDay"] = 0
    else:
        # Get popularity and hits per day
        popularity_partition: tuple[str, str, str] = distro_info["popularity"].partition(" ")
        distro_info["popularity"] = int(popularity_partition[0])
        distro_info["hitsPerDay"] = int(first_number.search(popularity_partition[2]).group())

    # Distro description
    distro_info["description"] = info_page.text.strip().partition("\n")[0]

    # Rating
    bold_text = info_page.find_all("b")
    distro_info["rating"] = 0
    distro_info["reviewCount"] = 0.0
    try:
        distro_info["rating"] = int(bold_text[-1].text)
        distro_info["reviewCount"] = float(bold_text[-2].text)
    except ValueError or KeyError:
        pass

    # Distro logo
    distro_info["logo"] = DISTOWATCH_URL + info_page.find("img", attrs={"class": "logo"}).get("src")
    logo: bytes = requests.get(
        url=distro_info["logo"],
        headers=REQUEST_HEADERS
    ).content

    # Extracted (current time)
    distro_info["extracted"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # Save json
    with open(f"{name}.json", "w") as json_file:
        json.dump(distro_info, json_file, sort_keys=True)

    # Save to json, image as png
    # Ubuntu: 2026-02-21 21:20


def main() -> None:
    # distros = get_distros()
    # print(len(distros))
    extract_distro_data("gnuinos")
    # extract_distro_data("eagle")
    # extract_distro_data("qlustar")


if __name__ == "__main__":
    main()
