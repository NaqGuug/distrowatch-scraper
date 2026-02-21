from bs4 import BeautifulSoup
import requests

# Constants
DISTOWATCH_URL: str = "https://distrowatch.com/"
URL_EXTENSION: str = "table.php?distribution="
REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla Gecko"
}


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
    distro_name: str = info_page.h1.text

    # Distro logo
    logo_url: str = info_page.find("img", attrs={"class": "logo"}).get("src")
    logo: bytes = requests.get(
        url=DISTOWATCH_URL+logo_url,
        headers=REQUEST_HEADERS
    ).content

    # Distro description
    distro_description: str = ""
    distro_description_list: str = info_page.find_all(string=True, recursive=False)
    for s in distro_description_list:
        striped_string: str = s.strip()
        if striped_string:
            distro_description = striped_string
            break
    # distro_description: str = info_page.text.strip()
    # print(distro_description)

    # TODO: Scrape list, popularity (12, 6, 3, 4, 1), reviews
    # Save to json, image as png



def main() -> None:
    # distros = get_distros()
    # print(len(distros))
    # extract_distro_data("gnuinos")
    extract_distro_data("0linux")


if __name__ == "__main__":
    main()
