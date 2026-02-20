#!/usr/bin/env python3
"""Build packages using CMake"""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Build packages using CMake")
    parser.add_argument("--cmake", required=True, help="Path to CMakeLists.txt directory")
    parser.add_argument("--build_dir", required=False, help="Base build output directory (default: <cmake_dir>/build)")
    parser.add_argument("--preset", action="append", default=[], help="Build preset (can be specified multiple times)")
    parser.add_argument("--build_type", action="append", default=[], help="Build type (can be specified multiple times)")
    parser.add_argument("--package", action="append", default=[], help="Package to build (can be specified multiple times)")

    args = parser.parse_args()

    cmake_dir = Path(args.cmake).resolve()
    base_build_dir = Path(args.build_dir).resolve() if args.build_dir else (cmake_dir / "build")
    presets = args.preset if args.preset else ["default"]
    build_types = args.build_type if args.build_type else ["Release"]
    packages = args.package

    packages_str = ";".join(packages) if packages else ""

    for preset in presets:
        for build_type in build_types:
            build_dir = base_build_dir / f"{preset}" / f"{build_type}"
            build_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n=== Configuring: preset={preset}, build_type={build_type}, packages={packages_str} ===")

            # Configure
            configure_cmd = [
                "cmake",
                "-G", "Ninja",
                "-S", str(cmake_dir),
                "-B", str(build_dir),
                f"-DCMAKE_BUILD_TYPE={build_type}",
                f"-DARIEO_PRESET={preset}",
            ]

            result = subprocess.run(configure_cmd)
            if result.returncode != 0:
                print(f"Configure failed for preset={preset}, build_type={build_type}")
                return result.returncode

            print(f"\n=== Building: preset={preset}, build_type={build_type}, packages={packages_str} ===")

            # Build
            build_cmd = [
                "cmake",
                "--build", str(build_dir),
            ]
            # Add all packages as a single --target argument (space-separated)
            if packages:
                build_cmd.extend(["--target"] + packages)

            result = subprocess.run(build_cmd)
            if result.returncode != 0:
                print(f"Build failed for preset={preset}, build_type={build_type}")
                return result.returncode

    print("\n=== All builds completed successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
