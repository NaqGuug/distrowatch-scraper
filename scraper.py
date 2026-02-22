from bs4 import BeautifulSoup
import requests
import re

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

    # Distro full name
    distro_name: str = info_page.h1.extract().text

    # Last update
    last_update: str = info_page.h2.extract().text

    # Distro logo
    logo_url: str = info_page.find("img", attrs={"class": "logo"}).get("src")
    logo: bytes = requests.get(
        url=DISTOWATCH_URL+logo_url,
        headers=REQUEST_HEADERS
    ).content

    # Info list (ul)
    distro_info_soup: BeautifulSoup = info_page.ul.extract()
    distro_info: dict[str, str | int] = {}
    for li in distro_info_soup.find_all("li"):
        # Key
        key: str = li.b.text.lower().replace(" ", "_")[:-1]

        # Value
        links = li.find_all(["a", "font"], recursive=False)
        value: str = ", ".join([link.text for link in links])

        distro_info[key] = value

    # Manual edits to status and popularity
    distro_info["status"] = distro_info["status"].partition(",")[0]
    if not distro_info["popularity"]:
        # Popularity not ranked
        distro_info["popularity"] = 0
        distro_info["hits_per_day"] = 0
    else:
        # Get popularity and hits per day
        popularity_partition: tuple[str, str, str] = distro_info["popularity"].partition(" ")
        distro_info["popularity"] = int(popularity_partition[0])
        distro_info["hits_per_day"] = int(first_number.search(popularity_partition[2]).group())

    # Distro description
    distro_description: str = info_page.text.strip().partition("\n")[0]

    # Rating
    bold_text = info_page.find_all("b")
    review_count: int = 0
    average_rating: float = 0.0
    try:
        review_count = int(bold_text[-1].text)
        average_rating = float(bold_text[-2].text)
    except ValueError or KeyError:
        pass

    # Save to json, image as png



def main() -> None:
    # distros = get_distros()
    # print(len(distros))
    extract_distro_data("gnuinos")
    # extract_distro_data("eagle")
    # extract_distro_data("qlustar")


if __name__ == "__main__":
    main()
