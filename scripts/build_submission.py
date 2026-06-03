#!/usr/bin/env python3
"""
Package main.py + orbit_lite/ into submission.tar.gz for Kaggle.

Usage:
    python scripts/build_submission.py
    python scripts/build_submission.py --output my_submission.tar.gz
    python scripts/build_submission.py --verify  # list contents after build
"""

import argparse
import os
import sys
import tarfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_submission(output_path: str, verify: bool = False):
    main_py = os.path.join(PROJECT_ROOT, "main.py")
    orbit_lite_dir = os.path.join(PROJECT_ROOT, "orbit_lite")

    # Validate required files exist
    if not os.path.isfile(main_py):
        print("ERROR: main.py not found at project root.")
        sys.exit(1)
    if not os.path.isdir(orbit_lite_dir):
        print("ERROR: orbit_lite/ directory not found at project root.")
        sys.exit(1)

    # Build the tarball
    with tarfile.open(output_path, "w:gz") as tar:
        # Add main.py at the archive root
        tar.add(main_py, arcname="main.py")

        # Add orbit_lite/ directory
        for root, dirs, files in os.walk(orbit_lite_dir):
            # Skip __pycache__
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith(".pyc"):
                    continue
                full_path = os.path.join(root, f)
                arcname = os.path.relpath(full_path, PROJECT_ROOT)
                tar.add(full_path, arcname=arcname)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"✅ Built {output_path} ({size_kb:.1f} KB)")

    if verify:
        print("\nContents:")
        with tarfile.open(output_path, "r:gz") as tar:
            for member in tar.getmembers():
                print(f"  {member.name}")


def main():
    parser = argparse.ArgumentParser(description="Build Kaggle submission archive")
    parser.add_argument(
        "--output", "-o",
        default=os.path.join(PROJECT_ROOT, "submission.tar.gz"),
        help="Output path (default: submission.tar.gz)",
    )
    parser.add_argument(
        "--verify", "-v",
        action="store_true",
        help="List archive contents after building",
    )
    args = parser.parse_args()

    build_submission(args.output, verify=args.verify)


if __name__ == "__main__":
    main()
