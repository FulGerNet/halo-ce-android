"""Shared source inputs and optimization helpers for the Android build."""
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

XDK_INCLUDE = Path("port/include/xdk")
MUSL_MATH_DIR = Path("port/third_party/musl-math")
MINIUPNPC_DIR = Path("port/third_party/miniupnpc")
MINIUPNPC_DEFINES = ["-DMINIUPNP_STATICLIB", "-DMINIUPNPC_SET_SOCKET_TIMEOUT", "-DMINIUPNPC_GET_SRC_ADDR",
                     "-D_BSD_SOURCE", "-D_DEFAULT_SOURCE"]
PGO_DIR = Path("pgo")
ANDROID_PROFILE = PGO_DIR / "halo_android.profdata"
PROFILE_LLVM_MAJOR = 22
PROFILE_USE_FLAGS = ["-Wno-profile-instr-unprofiled", "-Wno-profile-instr-out-of-date",
                     "-Wno-profile-instr-missing", "-Wno-backend-plugin"]
_clang_majors: Dict[str, Optional[int]] = {}


def xdk_headers() -> List[Path]:
    return sorted(XDK_INCLUDE.glob("*.h"))

def game_sources(config: Dict[str, Any]) -> List[Path]:
    """the game's C sources (port.json "game"): every one under its root but
    those excluded"""
    game = config["game"]
    excluded = set(game.get("exclude", []))
    return sorted(
        source for source in Path(game["root"]).rglob("*.c")
        if source.as_posix() not in excluded
    )

def game_defines_and_includes(config: Dict[str, Any]) -> str:
    """the game sources' defines and include directories (port.json "game")"""
    game = config["game"]
    return " ".join(
        [f"-D{define}" for define in game.get("defines", [])]
        + [f"-I{_quote(Path(directory))}" for directory in game.get("include_dirs", [])]
    )

def compile_launcher(sln: Any) -> str:
    """what the native ports' compile commands start with: the
    --compiler-launcher (ccache, say) and a space, or nothing"""
    launcher = getattr(sln, "compiler_launcher", None)
    return f"{launcher} " if launcher else ""

def miniupnpc_sources() -> List[Path]:
    """miniupnpc's library sources (port/third_party/miniupnpc/src)"""
    return sorted((MINIUPNPC_DIR / "src").glob("*.c"))

def musl_math_sources() -> List[Path]:
    """musl's maths functions the game uses (port/third_party/musl-math)"""
    return sorted((MUSL_MATH_DIR / "src").glob("*.c"))

def clang_major(cc: str) -> Optional[int]:
    """the major version of the clang named cc, or None if unknown"""
    if cc not in _clang_majors:
        try:
            output = subprocess.run([cc, "--version"], capture_output=True, text=True, check=False).stdout
            match = re.search(r"clang version (\d+)", output)
            _clang_majors[cc] = int(match.group(1)) if match else None
        except OSError:
            _clang_majors[cc] = None
    return _clang_majors[cc]

def pgo_mode(sln: Any) -> str:
    """use or off (configure.py --pgo)"""
    return getattr(sln, "port_pgo", "use")

def pgo_profile(sln: Any, own: Optional[Path], others: Sequence[Path], cc: str) -> Optional[Path]:
    """Select a supported profile, or skip it when optimization is disabled."""
    explicit = getattr(sln, "port_pgo_profile", None)
    if explicit:
        return explicit
    mode = pgo_mode(sln)
    if mode == "off":
        return None
    major = clang_major(cc)
    if major is not None and major < PROFILE_LLVM_MAJOR:
        print(f"{cc} is clang {major}; the profiles in {PGO_DIR} need clang {PROFILE_LLVM_MAJOR}: "
              "building without profile-guided optimisation", file=sys.stderr)
        return None
    for profile in ([own] if own else []) + list(others):
        if profile.is_file():
            return profile
    return None

def profile_use_flags(profile: Any) -> List[str]:
    return [f"-fprofile-use={_quote(profile)}", *PROFILE_USE_FLAGS] if profile else []

def _quote(path: Any) -> str:
    text = str(path).replace(os.sep, "/")
    return f'"{text}"' if " " in text else text


def updater_defines(release: bool) -> str:
    """the self-updater's build (port/shared/src/updater.c): its number, from
    HALO_BUILD_NUMBER (tools/ci_build.py gives it for builds of main; none
    elsewhere, which never look for updates), and its configuration"""
    number = os.environ.get("HALO_BUILD_NUMBER", "0")
    if not number.isdigit():
        number = "0"
    flavor = "release" if release else "debug"
    return f'-DHALO_BUILD_NUMBER={number} -DHALO_BUILD_FLAVOR=\\"{flavor}\\"'
