#!/usr/bin/env python3
"""
Validate Mermaid diagrams using mermaid-cli (mmdc).

Usage:
    python validate_mermaid.py <mermaid_code>
    python validate_mermaid.py --file <path_to_file>

Exit codes:
    0 - Valid
    1 - Syntax error
    2 - mmdc not found
    3 - Other error
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def validate_mermaid(mermaid_code: str) -> tuple[bool, str]:
    """
    Validate Mermaid code using mmdc.

    Returns:
        (is_valid, error_message)
    """
    # Check if mmdc is available
    try:
        subprocess.run(
            ["mmdc", "--version"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "mmdc (mermaid-cli) is not installed or not in PATH"

    # Create temp file with mermaid code
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".mmd",
        delete=False,
    ) as f:
        f.write(mermaid_code)
        temp_input = f.name

    # Create temp output file
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        temp_output = f.name

    try:
        # Run mmdc
        result = subprocess.run(
            ["mmdc", "-t", "neutral", "-i", temp_input, "-o", temp_output],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Parse error for useful information
            error_msg = result.stderr or result.stdout or "Unknown error"
            return False, error_msg

        return True, ""

    finally:
        # Clean up temp files
        Path(temp_input).unlink(missing_ok=True)
        Path(temp_output).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Mermaid diagrams using mermaid-cli"
    )
    parser.add_argument(
        "mermaid_code",
        nargs="?",
        help="Mermaid code to validate (use --file instead for file input)",
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to file containing Mermaid code",
    )

    args = parser.parse_args()

    # Get mermaid code from file or argument
    if args.file:
        mermaid_code = Path(args.file).read_text()
    elif args.mermaid_code:
        mermaid_code = args.mermaid_code
    else:
        # Read from stdin
        mermaid_code = sys.stdin.read()

    is_valid, error = validate_mermaid(mermaid_code)

    if is_valid:
        print("✓ Valid Mermaid diagram")
        sys.exit(0)
    else:
        print(f"✗ Invalid Mermaid diagram:")
        print(error)
        sys.exit(1)


if __name__ == "__main__":
    main()
