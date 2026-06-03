#!/usr/bin/env python3
"""
Submit to the Orbit Wars Kaggle competition and check status.

Usage:
    python scripts/submit.py -m "Producer v1"
    python scripts/submit.py -m "Tweaked regroup" --build   # build + submit
    python scripts/submit.py --status                       # check latest submission
"""

import argparse
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPETITION = "orbit-wars"

# Try to find kaggle CLI
KAGGLE_CLI = None
for candidate in [
    "kaggle",
    os.path.expanduser("~/Library/Python/3.9/bin/kaggle"),
    os.path.expanduser("~/Library/Python/3.11/bin/kaggle"),
    os.path.expanduser("~/Library/Python/3.12/bin/kaggle"),
]:
    if os.path.isfile(candidate) or subprocess.run(
        ["which", candidate], capture_output=True
    ).returncode == 0:
        KAGGLE_CLI = candidate
        break


def run_kaggle(*args):
    """Run a kaggle CLI command and return the output."""
    if KAGGLE_CLI is None:
        print("ERROR: kaggle CLI not found. Install with: pip install kaggle")
        sys.exit(1)
    cmd = [KAGGLE_CLI] + list(args)
    print(f"  → {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        # Filter out the urllib3 warning noise
        for line in result.stderr.splitlines():
            if "NotOpenSSLWarning" not in line and "warnings.warn" not in line:
                print(line, file=sys.stderr)
    return result


def submit(submission_file: str, message: str):
    """Submit a file to the competition."""
    if not os.path.isfile(submission_file):
        print(f"ERROR: Submission file not found: {submission_file}")
        print("Run 'python scripts/build_submission.py' first.")
        sys.exit(1)

    size_kb = os.path.getsize(submission_file) / 1024
    print(f"\n📦 Submitting {submission_file} ({size_kb:.1f} KB)")
    print(f"📝 Message: {message}\n")

    result = run_kaggle(
        "competitions", "submit", COMPETITION,
        "-f", submission_file,
        "-m", message,
    )

    if result.returncode != 0:
        print("\n❌ Submission failed!")
        sys.exit(1)

    print("\n✅ Submission successful!")
    print("\nChecking status...")
    check_status()


def check_status():
    """Check latest submission status."""
    print(f"\n📊 Latest submissions for {COMPETITION}:")
    run_kaggle("competitions", "submissions", COMPETITION)


def main():
    parser = argparse.ArgumentParser(description="Submit to Orbit Wars on Kaggle")
    parser.add_argument(
        "-m", "--message",
        default=None,
        help="Submission message (required for submit)",
    )
    parser.add_argument(
        "-f", "--file",
        default=os.path.join(PROJECT_ROOT, "submission.tar.gz"),
        help="Submission file (default: submission.tar.gz)",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Run build_submission.py before submitting",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Just check submission status (no submit)",
    )
    args = parser.parse_args()

    if args.status:
        check_status()
        return

    if args.message is None:
        print("ERROR: -m/--message is required for submission.")
        print("Example: python scripts/submit.py -m 'Producer v1'")
        sys.exit(1)

    if args.build:
        print("🔨 Building submission archive first...\n")
        build_script = os.path.join(PROJECT_ROOT, "scripts", "build_submission.py")
        result = subprocess.run([sys.executable, build_script], cwd=PROJECT_ROOT)
        if result.returncode != 0:
            print("❌ Build failed!")
            sys.exit(1)
        print()

    submit(args.file, args.message)


if __name__ == "__main__":
    main()
