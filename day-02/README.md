# Day 02 – Downloads Folder Organizer

Part of my **#30DaysOfAutomation** challenge.

## The problem
My Downloads folder had hundreds of mixed files (PDFs, images, zips, installers). Cleaning it by hand takes a long time, so it never gets done.

## The solution
A Python script that sorts every file into a folder by **type** and **month**:

```
Downloads/
├── Documents/2026-11/report.pdf
├── Images/2026-10/photo.jpg
├── Installers/2026-09/setup.exe
└── Other/2026-11/unknown.xyz
```

## Features
- **Dry run by default**: shows what it will move before moving anything
- **Safe with duplicates**: renames to `file (1).pdf` instead of overwriting
- **Skips unfinished downloads** (`.crdownload`, `.part`, `.tmp`)
- **Logging**: every move is saved to `organizer.log`
- Works on Windows, macOS and Linux (uses `pathlib`)

## Tech used
Python 3 · `pathlib` · `shutil` · `datetime` · `logging` · `argparse`

## How to run
```bash
# 1. Preview only (moves nothing)
python organize_downloads.py

# 2. Really organize the files
python organize_downloads.py --apply

# Organize a different folder
python organize_downloads.py "C:/Users/me/Desktop/test" --apply
```

## Result
<!-- Add your before/after screenshots here -->
| Before | After |
| --- | --- |
| ![before](before.png) | ![after](after.png) |

## What I learned
- How to work with files and folders using `pathlib` and `shutil`
- Why a dry-run mode matters before automating anything that changes files
- Using `logging` instead of `print` to keep a record of what the script did