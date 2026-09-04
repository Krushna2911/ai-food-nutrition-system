from pathlib import Path
import argparse
import random
import shutil
from PIL import Image


def read_categories(category_file: Path):
    """
    Read UEC-Food100 category.txt.

    Expected format:
        id    name
        1     rice
        2     eels on rice
        ...
    """
    categories = {}

    with category_file.open("r", encoding="utf-8") as f:
        next(f, None)  # skip header

        for line in f:
            line = line.strip()

            if not line:
                continue

            parts = line.split("\t", 1)

            if len(parts) != 2:
                parts = line.split(maxsplit=1)

            if len(parts) != 2:
                continue

            class_id = int(parts[0])
            class_name = parts[1].strip()

            categories[class_id] = class_name

    return categories


def collect_annotations(dataset_root: Path):
    """
    Collect image paths and bounding boxes from UEC-Food100.

    UEC structure:
        UECFOOD100/
            category.txt
            1/
                bb_info.txt
                1.jpg
                2.jpg
                ...
            2/
                bb_info.txt
                ...
    """

    category_file = dataset_root / "category.txt"

    if not category_file.exists():
        raise FileNotFoundError(
            f"category.txt not found: {category_file}"
        )

    categories = read_categories(category_file)

    samples = []

    for category_id, category_name in categories.items():

        category_dir = dataset_root / str(category_id)

        if not category_dir.exists():
            print(
                f"Warning: category directory missing: "
                f"{category_dir}"
            )
            continue

        bb_file = category_dir / "bb_info.txt"

        if not bb_file.exists():
            print(
                f"Warning: bb_info.txt missing: "
                f"{bb_file}"
            )
            continue

        with bb_file.open("r", encoding="utf-8") as f:
            next(f, None)  # skip header

            for line in f:
                parts = line.strip().split()

                if len(parts) < 5:
                    continue

                image_id = parts[0]

                x1 = int(parts[1])
                y1 = int(parts[2])
                x2 = int(parts[3])
                y2 = int(parts[4])

                # UEC images are normally .jpg
                image_path = category_dir / f"{image_id}.jpg"

                if not image_path.exists():
                    # Try common alternatives
                    alternatives = [
                        category_dir / f"{image_id}.JPG",
                        category_dir / f"{image_id}.jpeg",
                        category_dir / f"{image_id}.JPEG",
                        category_dir / f"{image_id}.png",
                    ]

                    image_path = next(
                        (p for p in alternatives if p.exists()),
                        None
                    )

                if image_path is None:
                    print(
                        f"Warning: image not found "
                        f"for category {category_id}, "
                        f"image {image_id}"
                    )
                    continue

                samples.append(
                    {
                        "image_path": image_path,
                        "category_id": category_id,
                        "category_name": category_name,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    }
                )

    return samples, categories


def convert_bbox_to_yolo(
    x1,
    y1,
    x2,
    y2,
    image_width,
    image_height,
):
    """
    Convert UEC bounding box:

        x1, y1, x2, y2

    to YOLO format:

        class_id x_center y_center width height

    Values are normalized to 0-1.
    """

    # Clamp coordinates to image boundaries
    x1 = max(0, min(x1, image_width))
    x2 = max(0, min(x2, image_width))
    y1 = max(0, min(y1, image_height))
    y2 = max(0, min(y2, image_height))

    box_width = x2 - x1
    box_height = y2 - y1

    if box_width <= 0 or box_height <= 0:
        return None

    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2

    return (
        x_center / image_width,
        y_center / image_height,
        box_width / image_width,
        box_height / image_height,
    )


def create_output_directories(output_root: Path):
    for split in ["train", "val", "test"]:
        (output_root / "images" / split).mkdir(
            parents=True,
            exist_ok=True,
        )

        (output_root / "labels" / split).mkdir(
            parents=True,
            exist_ok=True,
        )


def convert_dataset(
    dataset_root: Path,
    output_root: Path,
    train_ratio=0.8,
    val_ratio=0.1,
    seed=42,
):
    print("Reading UEC-Food100 annotations...")

    samples, categories = collect_annotations(dataset_root)

    print(f"Categories found: {len(categories)}")
    print(f"Annotated samples found: {len(samples)}")

    if not samples:
        raise RuntimeError("No annotated samples found.")

    # Random but reproducible split
    random.seed(seed)
    random.shuffle(samples)

    total = len(samples)

    train_end = int(total * train_ratio)
    val_end = train_end + int(total * val_ratio)

    splits = {
        "train": samples[:train_end],
        "val": samples[train_end:val_end],
        "test": samples[val_end:],
    }

    print("\nSplit sizes:")
    for split_name, split_samples in splits.items():
        print(f"  {split_name}: {len(split_samples)}")

    create_output_directories(output_root)

    # UEC category IDs start at 1.
    # YOLO class IDs start at 0.
    class_mapping = {
        category_id: category_id - 1
        for category_id in categories
    }

    converted = 0
    skipped = 0

    for split_name, split_samples in splits.items():

        print(f"\nConverting {split_name} split...")

        for sample in split_samples:

            image_path = sample["image_path"]

            try:
                with Image.open(image_path) as image:
                    image_width, image_height = image.size

            except Exception as exc:
                print(
                    f"Skipping unreadable image "
                    f"{image_path}: {exc}"
                )
                skipped += 1
                continue

            yolo_bbox = convert_bbox_to_yolo(
                sample["x1"],
                sample["y1"],
                sample["x2"],
                sample["y2"],
                image_width,
                image_height,
            )

            if yolo_bbox is None:
                print(
                    f"Skipping invalid bounding box: "
                    f"{image_path}"
                )
                skipped += 1
                continue

            class_id = class_mapping[
                sample["category_id"]
            ]

            x_center, y_center, width, height = yolo_bbox

            # Keep original filename but make it unique
            # using the category ID.
            output_stem = (
                f"food{sample['category_id']}_"
                f"{image_path.stem}"
            )

            output_image = (
                output_root
                / "images"
                / split_name
                / f"{output_stem}{image_path.suffix.lower()}"
            )

            output_label = (
                output_root
                / "labels"
                / split_name
                / f"{output_stem}.txt"
            )

            shutil.copy2(image_path, output_image)

            with output_label.open(
                "w",
                encoding="utf-8",
            ) as f:
                f.write(
                    f"{class_id} "
                    f"{x_center:.6f} "
                    f"{y_center:.6f} "
                    f"{width:.6f} "
                    f"{height:.6f}\n"
                )

            converted += 1

    # Save class names
    names_file = output_root / "classes.txt"

    with names_file.open("w", encoding="utf-8") as f:
        for category_id in sorted(categories):
            f.write(
                f"{class_mapping[category_id]} "
                f"{categories[category_id]}\n"
            )

    print("\nConversion complete.")
    print(f"Converted: {converted}")
    print(f"Skipped:   {skipped}")
    print(f"Output:    {output_root}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert UEC-Food100 to YOLO format."
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to UECFOOD100 directory.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output YOLO dataset directory.",
    )

    args = parser.parse_args()

    convert_dataset(
        dataset_root=args.input,
        output_root=args.output,
    )


if __name__ == "__main__":
    main()