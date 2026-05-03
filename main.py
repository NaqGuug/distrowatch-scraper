import os
import asyncio
import aiohttp
import scraper
import json
from tqdm.asyncio import tqdm_asyncio
from collections import namedtuple


ExtractImages: type[tuple[bool, bool, bool]] = namedtuple(
    "ExtractImages",
    ["logos", "thumbnails", "screenshots", "force_update"],
    defaults=[False, False, False, False]
)


async def scrape(
    extract_directory: str = "./data",
    images: ExtractImages = ExtractImages(),
) -> None:
    os.makedirs(extract_directory, exist_ok=True)
    if images.logos: os.makedirs(extract_directory + "/logos", exist_ok=True)
    if images.thumbnails: os.makedirs(extract_directory + "/thumbnails", exist_ok=True)
    if images.screenshots: os.makedirs(extract_directory + "/screenshots", exist_ok=True)

    async with aiohttp.ClientSession() as session:
        # Get all distros
        distros_names: list[str] = await scraper.get_distros(session)
        distros_names = distros_names[:10]  # TODO: Remove

        # Extract data from distro pages
        tasks = [scraper.extract_distro_data(session, name) for name in distros_names]
        results = await tqdm_asyncio.gather(*tasks)

        # Write json file
        with open(f"{extract_directory}/distros.json", "w") as json_file:
            json.dump(results, json_file, indent=2)

        def add_image_task(
            task_list: list,
            distro_data: dict,
            image_type: str,
            force_update: bool = False
        ) -> None:
            task_list.append(
                scraper.extract_image(
                    session,
                    distro_data[image_type],
                    extract_directory + distro_data["localPaths"][image_type][1:],
                    force_update
                )
            )

        # Collect image links
        image_tasks = []
        for r in results:
            if images.logos and r["logo"]:
                add_image_task(image_tasks, r, "logo", images.force_update)
            if images.thumbnails and r["thumbnail"]:
                add_image_task(image_tasks, r, "thumbnail", images.force_update)
            if images.screenshots and r["screenshot"]:
                add_image_task(image_tasks, r, "screenshot", images.force_update)

        await tqdm_asyncio.gather(*image_tasks)


def main() -> None:
    asyncio.run(scrape(images=ExtractImages(True, True, True, True)))


if __name__ == "__main__":
    main()
