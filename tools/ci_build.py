#!/usr/bin/env python3
"""Build and package Android: python tools/ci_build.py android release."""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(command, cwd=ROOT):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str, command)), cwd=cwd, check=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("platform", choices=["android"])
    parser.add_argument("config", choices=["debug", "release"])
    args = parser.parse_args()
    command = [sys.executable, "configure.py"]
    if args.config == "release":
        command.append("--release")
    else:
        command.append("--pgo=off")
    if os.environ.get("CI_COMPILER_LAUNCHER"):
        command += ["--compiler-launcher", os.environ["CI_COMPILER_LAUNCHER"]]
    # Stable across the build and sync workflows; a fast-forward main only
    # gains commits. Owners may override this for manually published releases.
    if os.environ.get("GITHUB_ACTIONS") == "true":
        number = os.environ.get("HALO_BUILD_NUMBER", "")
        if not number.strip().isdigit():
            number = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=ROOT, text=True).strip()
        if not number.isdigit() or not 1 <= int(number) <= 2100000000:
            raise SystemExit("HALO_BUILD_NUMBER must be between 1 and 2100000000")
        os.environ["HALO_BUILD_NUMBER"] = number
        print("Android version code:", number, flush=True)
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
                summary.write(f"Android {args.config}: version code **{number}**; manual release tag `build-{number}`.\n")
    run(command)
    run(["ninja", "android"])
    if os.name == "nt":
        run([sys.executable, "tools/android_windows_gradle.py", args.config])
    else:
        run(["./gradlew", "--console=plain", f"assemble{args.config.capitalize()}"], ROOT / "port/android")
    dist = ROOT / "dist" / f"halo-android-{args.config}"
    dist.mkdir(parents=True, exist_ok=True)
    apk = ROOT / f"port/android/app/build/outputs/apk/{args.config}/app-{args.config}.apk"
    shutil.copy2(apk, dist / apk.name)
    for source, destination in [
        ("extract-xiso/LICENSE.TXT", "extract-xiso-LICENSE.txt"),
        ("miniupnpc/LICENSE", "miniupnpc-LICENSE.txt"),
        ("stb/LICENSE", "stb-LICENSE.txt"),
        ("monocypher/LICENCE.md", "monocypher-LICENCE.txt"),
        ("expat/COPYING", "expat-COPYING.txt")
    ]:
        shutil.copy2(ROOT / "port/third_party" / source, dist / destination)

    for license in (ROOT / "port/assets/fonts").glob("*-*.txt"):
        if "LICENSE" in license.name or "OFL" in license.name:
            shutil.copy2(license, dist / license.name)

if __name__ == "__main__":
    main()
