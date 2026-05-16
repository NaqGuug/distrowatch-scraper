import os
import asyncio
import aiohttp
import scraper
import json
from tqdm.asyncio import tqdm_asyncio
from typing import NamedTuple


class ExtractImages(NamedTuple):
    """Image extraction settings"""
    logos: bool = False
    thumbnails: bool = False
    screenshots: bool = False
    force_update: bool = False


async def scrape(
    extract_directory: str = "./data",
    json_file_name: str = "distros.json",
    images: ExtractImages = ExtractImages(),
    force_update: bool = False
) -> None:
    json_file_path: str = f"{extract_directory}/{json_file_name}"
    full_update: bool = not force_update and os.path.exists(json_file_path)
    os.makedirs(extract_directory, exist_ok=True)
    if images.logos: os.makedirs(extract_directory + "/logos", exist_ok=True)
    if images.thumbnails: os.makedirs(extract_directory + "/thumbnails", exist_ok=True)
    if images.screenshots: os.makedirs(extract_directory + "/screenshots", exist_ok=True)

    async with aiohttp.ClientSession() as session:
        # Get all distros
        distros_names: set[str] = await scraper.get_distros(session)
        # TODO: Remove
        while (len(distros_names) > 10):
            distros_names.pop()

        # Remove distros from list if found from json file
        pre_distro_data: list[dict] = []
        if full_update:
            with open(json_file_path, "r") as jf:
                pre_distro_data = json.load(jf)
            for pdd in pre_distro_data:
                distros_names.discard(pdd["slug"])

        # Extract data from distro pages
        tasks = [scraper.extract_distro_data(session, name) for name in distros_names]
        results = await tqdm_asyncio.gather(*tasks)

        # Write json file
        results.extend(pre_distro_data)
        with open(json_file_path, "w") as json_file:
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
