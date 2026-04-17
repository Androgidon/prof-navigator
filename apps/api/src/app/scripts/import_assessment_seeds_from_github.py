import argparse
import asyncio
import tempfile
from pathlib import Path

import httpx

from app.loaders.assessment_seed_loader import AssessmentSeedLoader

REQUIRED_FILES = [
    "assessment-engine-prd.md",
    "careerpath-100-professions.csv",
    "careerpath-profession-matrix-filled.csv",
    "careerpath-question-bank-blueprint.md",
    "careerpath-question-bank-template.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import assessment seeds from GitHub raw files")
    parser.add_argument("--repo", default="Androgidon/prof-navigator")
    parser.add_argument("--ref", default="main")
    parser.add_argument("--base-path", default="docs/ai-context/forTest")
    parser.add_argument("--timeout", type=float, default=30.0)
    return parser.parse_args()


async def download_seed_bundle(target_dir: Path, repo: str, ref: str, base_path: str, timeout: float) -> None:
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for name in REQUIRED_FILES:
            url = f"https://raw.githubusercontent.com/{repo}/{ref}/{base_path}/{name}"
            response = await client.get(url)
            response.raise_for_status()
            (target_dir / name).write_text(response.text, encoding="utf-8")


async def run() -> None:
    args = parse_args()
    with tempfile.TemporaryDirectory(prefix="assessment-seeds-") as temp_dir:
        root = Path(temp_dir)
        await download_seed_bundle(
            target_dir=root,
            repo=args.repo,
            ref=args.ref,
            base_path=args.base_path,
            timeout=args.timeout,
        )
        loader = AssessmentSeedLoader(root=root)
        await loader.load()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
