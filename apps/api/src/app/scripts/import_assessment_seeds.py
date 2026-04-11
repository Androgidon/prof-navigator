import asyncio
from argparse import ArgumentParser
from pathlib import Path

from app.loaders.assessment_seed_loader import AssessmentSeedLoader


def parse_args() -> Path:
    parser = ArgumentParser()
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parents[5] / "docs" / "ai-context" / "forTest",
    )
    args = parser.parse_args()
    return args.path


async def run(path: Path) -> None:
    loader = AssessmentSeedLoader(root=path)
    await loader.load()


def main() -> None:
    asyncio.run(run(parse_args()))


if __name__ == "__main__":
    main()
