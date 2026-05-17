import sys
from pathlib import Path
import asyncio
import aiohttp
import extractor
import json
from tqdm.asyncio import tqdm_asyncio
from typing import NamedTuple
import argparse


class ExtractImages(NamedTuple):
    """Image extraction settings"""
    logos: bool = False
    thumbnails: bool = False
    screenshots: bool = False
    force_update: bool = False


async def scrape(
    extract_directory: Path,
    json_file_name: str = "distros.json",
    images: ExtractImages = ExtractImages(),
    force_update: bool = False
) -> None:
    """Scrape DistroWatch.com"""
    json_file_path: Path = extract_directory / json_file_name
    full_update: bool = not force_update and json_file_path.is_file()
    extract_directory.mkdir(exist_ok=True)
    if images.logos: (extract_directory / "logos").mkdir(exist_ok=True)
    if images.thumbnails: (extract_directory / "thumbnails").mkdir(exist_ok=True)
    if images.screenshots: (extract_directory / "screenshots").mkdir(exist_ok=True)

    async with aiohttp.ClientSession() as session:
        # Get all distros
        name_result: list[set[str]] = await tqdm_asyncio.gather(extractor.get_distros(session))
        distros_names: set[str] = name_result[0]

        # Remove distros from list if found from json file
        pre_distro_data: list[dict] = []
        if full_update:
            with json_file_path.open("r") as jf:
                pre_distro_data = json.load(jf)
            for pdd in pre_distro_data:
                distros_names.discard(pdd["slug"])

        # Extract data from distro pages
        tasks = [extractor.extract_distro_data(session, name) for name in distros_names]
        results = await tqdm_asyncio.gather(*tasks)

        # Write json file
        results.extend(pre_distro_data)
        with json_file_path.open("w") as json_file:
            json.dump(results, json_file, indent=2)

        def add_image_task(
            task_list: list,
            distro_data: dict,
            image_type: str,
            force_update: bool = False
        ) -> None:
            task_list.append(
                extractor.extract_image(
                    session,
                    distro_data[image_type],
                    extract_directory / f"{image_type}s" / distro_data["localPaths"][image_type].rpartition("/")[-1],
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
    parser = argparse.ArgumentParser(
        description="Scrape distro information and images from DistroWatch.com"
    )
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("-f", "--force-update", action="store_true", help="Force update existing data")
    parser.add_argument("-i", "--images", action="store_true", help="Scrape all images")
    parser.add_argument("-l", "--logos", action="store_true", help="Scrape logos")
    parser.add_argument("-t", "--thumbnails", action="store_true", help="Scrape thumbnails")
    parser.add_argument("-s", "--screenshots", action="store_true", help="Scrape screenshots")
    args = parser.parse_args()

    # Check if output directory is valid
    output: Path | None = args.output and Path(args.output)
    if output and not output.is_dir():
        sys.exit(f"{Path(sys.argv[0]).name}: error: invalid path: {args.output}")

    # Image settings
    images = ExtractImages(
        logos=args.logos or args.images,
        thumbnails=args.thumbnails or args.images,
        screenshots=args.screenshots or args.images,
        force_update=args.force_update
    )

    # Scrape
    asyncio.run(scrape(
        extract_directory=output or Path("data"),
        images=images,
        force_update=args.force_update
    ))


if __name__ == "__main__":
    main()
