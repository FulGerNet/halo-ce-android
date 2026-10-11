#!/usr/bin/env python3

# Root build script: writes build.ninja for Android.

import argparse
import io
import os
import sys
from pathlib import Path
from types import SimpleNamespace

from tools import ninja_syntax
from tools.android_build import android_configure_inputs, generate_android_build
from tools.android_sources import check_profile_options

# arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--compiler-launcher",
    metavar="BINARY",
    help="a program that runs each compile, such as ccache "
    "(links and the Android host's few units run the compiler directly)",
)
parser.add_argument(
    "--release",
    action="store_true",
    help="Android release build: assertions are not checked",
)
parser.add_argument(
    "--profile",
    action="store_true",
    help="profiling build: CPU scopes recorded on a console command or launch setting",
)
parser.add_argument(
    "--pgo",
    default="use",
    choices=["use", "off"],
    help="use the inherited optimization profile in pgo/ (clang 22+), or disable it",
)
parser.add_argument(
    "--pgo-profile",
    metavar="PROFDATA",
    type=Path,
    help="profile-guided optimisation from this profile instead",
)
parser.add_argument(
    "--android-ndk",
    type=str,
    help="Android NDK for `ninja android` (default: ANDROID_NDK_HOME, or the newest under the Android SDK)",
)
parser.add_argument(
    "--android-guest-cc",
    type=str,
    help="clang with the arm64_32 target for the Android guest (default: clang)",
)
args = parser.parse_args()
try:
    check_profile_options(args.profile, args.pgo)
except ValueError as error:
    parser.error(str(error))

# the settings the builds read
sln = SimpleNamespace(
    build_dir=Path("build"),
    compiler_launcher=args.compiler_launcher,
    port_release=args.release,
    port_profile=args.profile,
    port_pgo=args.pgo,
    port_pgo_profile=args.pgo_profile,
    android_ndk=args.android_ndk,
    android_guest_cc=args.android_guest_cc,
)


# build.ninja
out = io.StringIO()
n = ninja_syntax.Writer(out)
n.variable("ninja_required_version", "1.3")
n.newline()

configure_script = Path(os.path.relpath(os.path.abspath(sys.argv[0])))
n.comment("The arguments passed to configure.py, for rerunning it.")
n.variable(
    "configure_args",
    [f'"{arg}"' if any(ch.isspace() for ch in arg) else arg for arg in sys.argv[1:]],
)
n.variable("python", f'"{Path(sys.executable).as_posix()}"')
n.newline()

generate_android_build(n, sln)

n.comment("Reconfigure on change")
n.rule(
    name="configure",
    command=f"$python {configure_script} $configure_args",
    generator=True,
    description=f"RUN {configure_script}",
)
n.build(
    outputs="build.ninja",
    rule="configure",
    implicit=[
        configure_script,
        Path("tools/ninja_syntax.py"),
        *android_configure_inputs(),
    ],
)
n.newline()

# Build the Android APK by default.
if "\nbuild android_apk: " in out.getvalue():
    n.default("android_apk")
else:
    raise SystemExit("Android build unavailable: install the NDK and check dependency downloads.")

with open("build.ninja", "w", encoding="utf-8") as f:
    f.write(out.getvalue())
out.close()
