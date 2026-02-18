#!/usr/bin/env python3
"""
ArieoEngine Package Gatherer
Gathers all ArieoPackage.yaml files into .cache folder based on packages.manifest.yaml
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Tuple, Optional
import yaml


def get_script_dir():
    """Get the directory where this script is located."""
    return Path(os.path.dirname(os.path.abspath(__file__)))


def load_manifest(manifest_file_path=None):
    """
    Load package manifest file (YAML format)
    
    Args:
        manifest_file_path: Optional path to manifest file. If not provided, uses "packages.manifest.yaml"
    
    Returns:
        dict: Manifest data or None if failed
    """
    if not manifest_file_path:
        yaml_path = Path("packages.manifest.yaml")
        
        if yaml_path.exists():
            manifest_path = yaml_path
        else:
            error_msg = "✗ Error: packages.manifest.yaml not found"
            print(error_msg)
            sys.exit(1)
    else:
        manifest_path = Path(manifest_file_path)
        if not manifest_path.exists():
            error_msg = f"✗ Error: Manifest file not found at {manifest_path}"
            print(error_msg)
            sys.exit(1)
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f) or {}
            manifest['_manifest_dir'] = str(manifest_path.parent.resolve())
            return manifest
    except Exception as e:
        error_msg = f"✗ Error: Failed to read manifest file: {e}"
        print(error_msg)
        sys.exit(1)


def verify_yaml(yaml_path: Path, verbose: bool = False) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Verify that a YAML file is valid and contains required fields.
    
    Args:
        yaml_path: Path to the YAML file
        verbose: Enable verbose output
        
    Returns:
        Tuple of (is_valid, parsed_data, error_message)
    """
    if not yaml_path.exists():
        return False, None, f"File does not exist: {yaml_path}"
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if file is empty
        if not content.strip():
            return False, None, "YAML file is empty"
        
        # Try to parse the YAML
        data = yaml.safe_load(content)
        
        if data is None:
            return False, None, "YAML file is empty or contains only comments"
        
        if not isinstance(data, dict):
            return False, None, f"YAML root must be a dictionary, got {type(data).__name__}"
        
        # Check for required 'name' field
        if 'name' not in data:
            return False, None, "Missing required field: 'name'"
        
        if not data['name'] or not isinstance(data['name'], str):
            return False, None, "Field 'name' must be a non-empty string"
        
        if verbose:
            print(f"  ✓ Valid YAML: {yaml_path.name} (name: {data['name']})")
        
        return True, data, None
        
    except yaml.YAMLError as e:
        return False, None, f"YAML syntax error: {e}"
    except Exception as e:
        return False, None, f"Error reading file: {e}"


def gather_packages_from_manifest(manifest: dict, cache_dir: Path, clean: bool = False, verbose: bool = False) -> int:
    """
    Gather ArieoPackage.yaml files based on packages list in manifest.
    
    Args:
        manifest: Loaded manifest dictionary
        cache_dir: Destination .cache folder
        clean: Clean cache folder before gathering
        verbose: Enable verbose output
        
    Returns:
        int: Number of packages gathered
    """
    manifest_dir = Path(manifest.get('_manifest_dir', '.')).resolve()
    packages_list = manifest.get('packages', [])
    
    if not packages_list:
        print("No packages defined in manifest.")
        return 0
    
    # Clean cache directory if requested
    if clean and cache_dir.exists():
        if verbose:
            print(f"Cleaning cache directory: {cache_dir}")
        shutil.rmtree(cache_dir)
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nProcessing {len(packages_list)} package entries from manifest...")
    
    copied_count = 0
    skipped_count = 0
    error_count = 0
    
    for idx, entry in enumerate(packages_list, 1):
        # Handle local entries
        if 'local' in entry:
            local_path = entry['local']
            # Expand ${CUR_MANIFEST_FILE_DIR} variable
            local_path = local_path.replace('${CUR_MANIFEST_FILE_DIR}', str(manifest_dir))
            local_path = os.path.expandvars(local_path)
            package_path = Path(local_path).resolve()
        elif 'git' in entry:
            # Skip git entries (would need to clone first)
            git_url = entry['git']
            url_part = git_url.split('@')[0]
            repo_name = url_part.rstrip('/').split('/')[-1].replace('.git', '')
            if verbose:
                print(f"  [{idx}/{len(packages_list)}] Skipping git entry: {repo_name} (not cloned)")
            skipped_count += 1
            continue
        else:
            print(f"  [{idx}/{len(packages_list)}] ✗ Unknown entry format: {entry}")
            error_count += 1
            continue
        
        # Check if package folder exists
        if not package_path.exists():
            print(f"  [{idx}/{len(packages_list)}] ✗ Package folder not found: {package_path}")
            error_count += 1
            continue
        
        # Find ArieoPackage.yaml in the package folder
        arieo_yaml_path = package_path / 'ArieoPackage.yaml'
        
        if not arieo_yaml_path.exists():
            print(f"  [{idx}/{len(packages_list)}] ✗ ArieoPackage.yaml not found in: {package_path}")
            error_count += 1
            continue
        
        # Verify the YAML file and get package name from it
        is_valid, pkg_data, error_msg = verify_yaml(arieo_yaml_path, verbose=False)
        
        if not is_valid:
            print(f"  [{idx}/{len(packages_list)}] ✗ Invalid YAML: {error_msg}")
            error_count += 1
            continue
        
        # Get package name from ArieoPackage.yaml
        pkg_name = pkg_data['name']
        
        # Create destination folder: .cache/[PackageName]/
        dest_folder = cache_dir / pkg_name
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        # Copy to .cache/[PackageName]/ArieoPackage.yaml
        dest_path = dest_folder / 'ArieoPackage.yaml'
        
        shutil.copy2(arieo_yaml_path, dest_path)
        copied_count += 1
        
        if verbose:
            print(f"  [{idx}/{len(packages_list)}] ✓ {pkg_name} -> {dest_path.relative_to(cache_dir)}")
        else:
            print(f"  [{idx}/{len(packages_list)}] ✓ {pkg_name}")
    
    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Copied:  {copied_count}")
    print(f"  Skipped: {skipped_count} (git entries)")
    print(f"  Errors:  {error_count}")
    print(f"{'='*60}")
    
    return copied_count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ArieoEngine Package Gatherer - Gathers all ArieoPackage.yaml files into .cache folder',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--manifest',
        dest='manifest_file',
        default=None,
        help='Path to packages.manifest.yaml'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean the .cache folder before gathering'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    print("ArieoEngine Package Gatherer")
    print("=" * 60)
    
    # Load manifest first to get cache folder path
    manifest = load_manifest(args.manifest_file)
    manifest_dir = Path(manifest.get('_manifest_dir', '.')).resolve()
    
    # Get cache folder from manifest, expand variables
    cache_folder_raw = manifest.get('pachages_cache_folder', './.cache')
    cache_folder_expanded = cache_folder_raw.replace('${CUR_MANIFEST_FILE_DIR}', str(manifest_dir))
    cache_folder_expanded = os.path.expandvars(cache_folder_expanded)
    
    # Resolve relative paths against manifest directory
    cache_path = Path(cache_folder_expanded)
    if not cache_path.is_absolute():
        cache_path = manifest_dir / cache_path
    cache_dir = cache_path.resolve()
    
    if args.verbose:
        print(f"Manifest directory: {manifest_dir}")
        print(f"Cache directory: {cache_dir}")
    
    count = gather_packages_from_manifest(manifest, cache_dir, args.clean, args.verbose)
    
    print(f"\n{'='*60}")
    if count > 0:
        print(f"✓ Package gathering complete: {count} package(s) in {cache_dir}")
    else:
        print("✗ No packages gathered")
    print(f"{'='*60}")
    
    sys.exit(0 if count > 0 else 1)


if __name__ == '__main__':
    main()
