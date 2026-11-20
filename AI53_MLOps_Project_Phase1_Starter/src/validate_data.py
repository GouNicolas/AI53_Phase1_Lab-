from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

EXPECTED_SPLITS = {"train": 1034, "validation": 133, "test": 128}
EXPECTED_CLASSES = {"angular_leaf_spot", "bean_rust", "healthy"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def validate_dataset(raw_root: Path) -> dict:
    """Validate the raw dataset and return a deterministic quality report.
    
    Raises if the dataset structure, image counts, or image readability is invalid.
    Returns only a deterministic JSON-serializable PASS report on success.
    """
    if not raw_root.is_dir():
        raise FileNotFoundError(f"Raw dataset directory is missing: {raw_root}")

    expected_splits = set(EXPECTED_SPLITS)
    actual_splits = {path.name for path in raw_root.iterdir() if path.is_dir()}
    if actual_splits != expected_splits:
        raise RuntimeError(
            f"Invalid splits: expected {sorted(expected_splits)}, "
            f"got {sorted(actual_splits)}"
        )

    report_splits: dict[str, dict] = {}
    total_images = 0

    for split in ("train", "validation", "test"):
        split_path = raw_root / split
        if not split_path.is_dir():
            raise RuntimeError(f"Missing required split: {split}")

        actual_classes = {
            path.name for path in split_path.iterdir() if path.is_dir()
        }
        if actual_classes != EXPECTED_CLASSES:
            raise RuntimeError(
                f"Invalid classes in split '{split}': "
                f"expected {sorted(EXPECTED_CLASSES)}, got {sorted(actual_classes)}"
            )

        class_counts: dict[str, int] = {}
        split_total = 0

        for class_name in sorted(EXPECTED_CLASSES):
            class_path = split_path / class_name
            if not class_path.is_dir():
                raise RuntimeError(
                    f"Missing required class '{class_name}' in split '{split}'"
                )

            image_files = sorted(
                path for path in class_path.rglob("*")
                if path.is_file()
            )
            if not image_files:
                raise RuntimeError(
                    f"Class '{class_name}' in split '{split}' is empty"
                )

            for image_file in image_files:
                suffix = image_file.suffix.lower()
                if suffix and suffix not in IMAGE_EXTENSIONS:
                    raise RuntimeError(f"Invalid image extension: {image_file}")
                with Image.open(image_file) as img:
                    img.load()

            count = len(image_files)
            class_counts[class_name] = count
            split_total += count

        expected_count = EXPECTED_SPLITS[split]
        if split_total != expected_count:
            raise RuntimeError(
                f"Image count mismatch in split '{split}': "
                f"expected {expected_count}, got {split_total}"
            )

        report_splits[split] = {
            "images": split_total,
            "class_counts": class_counts,
        }
        total_images += split_total

    return {
        "status": "PASS",
        "classes": sorted(EXPECTED_CLASSES),
        "splits": report_splits,
        "total_images": total_images,
    }


def main() -> None:
    report = validate_dataset(Path("data/raw"))
    Path("reports").mkdir(exist_ok=True)
    Path("reports/data_quality.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
