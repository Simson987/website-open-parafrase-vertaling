#!/usr/bin/env python3
"""Toon basisdekking en voortgang van inhoudelijk gekozen hoofdstukbeelden."""

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--missing", action="store_true", help="Toon ook ieder onvolledig hoofdstuk")
    args = parser.parse_args()

    editions = json.loads((ROOT / "data/vertalingen/manifest.json").read_text(encoding="utf-8"))["edities"]
    published = set(next(edition["boeken"] for edition in editions if edition["code"] == "nl-opv"))
    images = json.loads((ROOT / "data/book-images.json").read_text(encoding="utf-8"))["books"]
    plan_path = ROOT / "data/chapter-image-plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else {}
    minimum = plan.get("minimum_images_per_chapter", 3)
    counts = Counter((book, scene["chapter"]) for book, scenes in images.items() for scene in scenes)
    chapters = [
        (book, int(path.stem))
        for book in sorted(published)
        for path in (ROOT / "data/vertalingen/nl-opv" / book).glob("*.json")
        if path.stem.isdigit()
    ]
    missing = [(book, chapter, minimum - counts[book, chapter]) for book, chapter in chapters if counts[book, chapter] < minimum]
    reviewed = plan.get("chapters", [])
    chapter_set = set(chapters)
    targets = {}
    for item in reviewed:
        key = item["book"], item["chapter"]
        if key not in chapter_set or key in targets or item["target_images"] < minimum:
            raise ValueError(f"Ongeldig of dubbel hoofdstukdoel: {item}")
        targets[key] = item["target_images"]
    planned_missing = [(book, chapter, target - counts[book, chapter])
                       for (book, chapter), target in targets.items() if counts[book, chapter] < target]
    report = {
        "books": len(published),
        "chapters": len(chapters),
        "chapters_with_three_images": sum(counts[key] == 3 for key in chapters),
        "chapters_with_at_least_three_images": sum(counts[key] >= 3 for key in chapters),
        "chapters_with_more_than_three_images": sum(counts[key] > 3 for key in chapters),
        "images": sum(counts.values()),
        "images_still_needed": sum(item[2] for item in missing),
        "chapters_reviewed_for_expansion": len(reviewed),
        "reviewed_chapters_at_target": len(reviewed) - len(planned_missing),
        "additional_images_needed_for_reviewed_chapters": sum(item[2] for item in planned_missing),
    }
    if args.missing:
        report["missing"] = [{"book": book, "chapter": chapter, "needed": needed} for book, chapter, needed in missing]
        report["planned_missing"] = [{"book": book, "chapter": chapter, "needed": needed}
                                     for book, chapter, needed in planned_missing]
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
