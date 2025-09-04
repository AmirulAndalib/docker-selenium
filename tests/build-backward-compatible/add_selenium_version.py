#!/usr/bin/env python3
import re
import sys
from pathlib import Path

import yaml


def add_selenium_version(version):
    """
    Add a new Selenium version configuration to selenium-matrix.yml

    Args:
        version (str): The Selenium version to add (e.g., '4.36.0')
    """
    # Validate version format
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print(f"Error: Version '{version}' is not in the correct format (e.g., 4.36.0)")
        sys.exit(1)

    matrix_file = Path(__file__).parent / 'selenium-matrix.yml'

    def replace_none(d):
        if isinstance(d, dict):
            return {k: replace_none(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [replace_none(x) for x in d]
        elif d is None:
            return []
        return d

    # Read the existing YAML file
    with open(matrix_file, 'r') as f:
        try:
            data = yaml.safe_load(f) or {}
            # Replace None values with empty strings
            data = replace_none(data)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            sys.exit(1)

    # Check if version already exists
    if version in data.get('matrix', {}).get('selenium', {}):
        print(f"Version {version} already exists in the matrix")
        sys.exit(0)

    # Create the new version entry
    new_entry = {
        'BASE_RELEASE': f'selenium-{version}',
        'BASE_VERSION': version,
        'VERSION': version,
        'BINDING_VERSION': version,
        'browser': [],
    }

    # Add the new version to the matrix
    data['matrix']['selenium'][version] = new_entry

    # Sort the selenium versions in descending order
    if 'selenium' in data['matrix']:
        sorted_selenium = {}
        # Get all versions, handle both string and numeric versions correctly
        versions = []
        for v in data['matrix']['selenium'].keys():
            try:
                # Convert version string to tuple of integers for proper numeric comparison
                ver_tuple = tuple(map(int, v.split('.'))) if v != 'nightly' else (float('inf'),)
                versions.append((ver_tuple, v))
            except (ValueError, AttributeError):
                # Fallback for non-numeric versions (like 'nightly')
                versions.append((v, v))

        # Sort in descending order, with 'nightly' first, then by version numbers
        versions.sort(reverse=True, key=lambda x: (x[0] == 'nightly', x[0]))

        # Rebuild the selenium dictionary in sorted order
        for ver_tuple, ver in versions:
            sorted_selenium[ver] = data['matrix']['selenium'][ver]

        data['matrix']['selenium'] = sorted_selenium

    # Write back to the file while preserving the original structure
    with open(matrix_file, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=1000)

    print(f"Successfully added Selenium version {version} to the matrix")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <version>")
        print("Example: python add_selenium_version.py 4.36.0")
        sys.exit(1)

    version = sys.argv[1].strip()
    add_selenium_version(version)
