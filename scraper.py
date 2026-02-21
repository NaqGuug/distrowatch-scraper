from bs4 import BeautifulSoup
import requests

# Constants
DISTOWATCH_URL: str = "https://distrowatch.com/"
REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla Gecko"
}


def get_distros() -> dict[str, str]:
    """Return map of all distros"""
    # Get DistroWatch main page
    main_page: str = requests.get(
        url=DISTOWATCH_URL,
        headers=REQUEST_HEADERS
    )
    soup = BeautifulSoup(main_page.text, "html.parser")

    # Get options from news page
    news_filtering: BeautifulSoup = soup.find(attrs={"class": "Introduction"})
    distro_select: BeautifulSoup = news_filtering.find("select", attrs={"name": "distribution"})
    # Get all distros
    distros: dict[str, str] = {}
    for options in distro_select.find_all("option"):
        if options.string == "All":
            # Default selection, not a distro
            continue
        # value: name, e.g. "acoros": "AçorOS"
        distros[options.get("value")] = options.string

    return distros


def main() -> None:
    distros = get_distros()
    print(len(distros))


if __name__ == "__main__":
    main()
