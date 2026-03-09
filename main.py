import os
import asyncio
import aiohttp
import scraper
import json
from tqdm.asyncio import tqdm_asyncio


async def main() -> None:
    os.makedirs(scraper.EXTRACT_DIRECTORY, exist_ok=True)
    os.makedirs(scraper.EXTRACT_DIRECTORY + "/logos", exist_ok=True)
    os.makedirs(scraper.EXTRACT_DIRECTORY + "/thumbnails", exist_ok=True)
    os.makedirs(scraper.EXTRACT_DIRECTORY + "/screenshots", exist_ok=True)

    async with aiohttp.ClientSession() as session:
        distros_names: list[str] = await scraper.get_distros(session)
        distros_names = distros_names[:50]
        tasks = [scraper.extract_distro_data(session, name) for name in distros_names]
        results = await tqdm_asyncio.gather(*tasks)

        with open(f"{scraper.EXTRACT_DIRECTORY}/distros.json", "w") as json_file:
            json.dump(results, json_file, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
