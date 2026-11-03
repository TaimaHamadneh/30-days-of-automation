"""
Day 2 - #30DaysOfAutomation
Organize a messy folder (like Downloads) by file type and month.

Before:  Downloads/report.pdf, photo.jpg, setup.exe ...
After:   Downloads/Documents/2026-11/report.pdf
         Downloads/Images/2026-10/photo.jpg
         Downloads/Installers/2026-09/setup.exe

Usage:
    python organize_downloads.py                  # dry run on your Downloads folder (moves nothing)
    python organize_downloads.py --apply          # really move the files
    python organize_downloads.py "D:/Some Folder" --apply
"""

import argparse
import logging
import shutil
from datetime import datetime
from pathlib import Path

# 1) Which extension goes to which folder. Add your own here.
CATEGORIES = {
    "Images":     {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".heic", ".bmp"},
    "Documents":  {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"},
    "Sheets":     {".xls", ".xlsx", ".csv", ".ods"},
    "Slides":     {".ppt", ".pptx", ".odp", ".key"},
    "Archives":   {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".apk"},
    "Videos":     {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Audio":      {".mp3", ".wav", ".m4a", ".flac", ".ogg"},
    "Code":       {".py", ".js", ".ts", ".html", ".css", ".json", ".ipynb", ".java", ".c", ".cpp", ".sql"},
}

# Files still downloading or temporary: never touch them.
SKIP_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}


def get_category(file: Path) -> str:
    ext = file.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"


def unique_destination(dest: Path) -> Path:
    """If report.pdf already exists, use report (1).pdf, report (2).pdf, ..."""
    if not dest.exists():
        return dest
    counter = 1
    while True:
        candidate = dest.with_name(f"{dest.stem} ({counter}){dest.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def organize(folder: Path, apply: bool) -> None:
    category_names = set(CATEGORIES) | {"Other"}
    moved = skipped = 0

    for file in folder.iterdir():
        # Only loose files: skip folders (including the ones we create) and hidden files.
        if not file.is_file() or file.name.startswith("."):
            continue
        if (file.suffix.lower() in SKIP_EXTENSIONS
                or file.name in {Path(__file__).name, "organizer.log"}):
            skipped += 1
            continue

        category = get_category(file)
        month = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m")
        dest = unique_destination(folder / category / month / file.name)

        if apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(dest))
            logging.info("MOVED   %s -> %s", file.name, dest.relative_to(folder))
        else:
            logging.info("WOULD MOVE  %s -> %s", file.name, dest.relative_to(folder))
        moved += 1

    mode = "Moved" if apply else "Would move"
    logging.info("Done. %s %d files, skipped %d.", mode, moved, skipped)
    if not apply:
        logging.info("This was a dry run. Add --apply to really move the files.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Organize a folder by file type and month.")
    parser.add_argument("folder", nargs="?", default=str(Path.home() / "Downloads"),
                        help="Folder to organize (default: your Downloads folder)")
    parser.add_argument("--apply", action="store_true", help="Really move files (default is dry run)")
    args = parser.parse_args()

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}")

    # Log to the screen AND to a file, so you have a record of every move.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(),
                  logging.FileHandler(folder / "organizer.log", encoding="utf-8")],
    )
    logging.info("Organizing: %s", folder)
    organize(folder, apply=args.apply)


if __name__ == "__main__":
    main()