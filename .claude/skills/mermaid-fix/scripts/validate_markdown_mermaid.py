#!/usr/bin/env python3
"""
Extract and validate Mermaid diagrams from Markdown files concurrently.

Usage:
    python validate_markdown_mermaid.py <markdown_file>
    python validate_markdown_mermaid.py <markdown_file> --workers 4

Exit codes:
    0 - All diagrams valid
    1 - One or more diagrams have syntax errors
    2 - mmdc not found
    3 - Other error
"""

import argparse
import asyncio
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List


@dataclass
class MermaidDiagram:
    """Represents a Mermaid diagram extracted from markdown."""
    index: int
    start_line: int
    end_line: int
    code: str


def extract_mermaid_diagrams(markdown_content: str) -> List[MermaidDiagram]:
    """
    Extract all Mermaid code blocks from markdown content.

    Args:
        markdown_content: The markdown file content

    Returns:
        List of MermaidDiagram objects
    """
    diagrams = []
    lines = markdown_content.split('\n')

    in_mermaid_block = False
    start_line = 0
    code_lines = []
    diagram_index = 0

    for i, line in enumerate(lines, start=1):
        # Check for mermaid code block start
        if line.strip() == '```mermaid':
            in_mermaid_block = True
            start_line = i
            code_lines = []
            continue

        # Check for code block end
        if in_mermaid_block and line.strip() == '```':
            in_mermaid_block = False
            diagram_index += 1
            diagrams.append(MermaidDiagram(
                index=diagram_index,
                start_line=start_line,
                end_line=i,
                code='\n'.join(code_lines)
            ))
            code_lines = []
            continue

        # Collect code inside mermaid block
        if in_mermaid_block:
            code_lines.append(line)

    return diagrams


def validate_single_diagram(diagram: MermaidDiagram) -> tuple[MermaidDiagram, bool, str]:
    """
    Validate a single Mermaid diagram using mmdc.

    Args:
        diagram: The MermaidDiagram to validate

    Returns:
        (diagram, is_valid, error_message)
    """
    # Check if mmdc is available
    try:
        subprocess.run(
            ["mmdc", "--version"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return diagram, False, "mmdc (mermaid-cli) is not installed or not in PATH"

    # Create temp files
    with NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
        f.write(diagram.code)
        temp_input = f.name

    with NamedTemporaryFile(suffix=".svg", delete=False) as f:
        temp_output = f.name

    try:
        # Run mmdc
        result = subprocess.run(
            ["mmdc", "-t", "neutral", "-i", temp_input, "-o", temp_output],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            error_msg = result.stderr or result.stdout or "Unknown error"
            return diagram, False, error_msg

        return diagram, True, ""

    finally:
        # Clean up temp files
        Path(temp_input).unlink(missing_ok=True)
        Path(temp_output).unlink(missing_ok=True)


def validate_markdown_file(
    markdown_path: str | Path,
    workers: int = 4
) -> tuple[List[MermaidDiagram], List[tuple[MermaidDiagram, str]]]:
    """
    Validate all Mermaid diagrams in a markdown file concurrently.

    Args:
        markdown_path: Path to the markdown file
        workers: Number of parallel workers for validation

    Returns:
        (all_diagrams, failed_diagrams_with_errors)
    """
    markdown_path = Path(markdown_path)
    content = markdown_path.read_text()

    diagrams = extract_mermaid_diagrams(content)

    if not diagrams:
        return [], []

    # Validate concurrently using ProcessPoolExecutor
    failed = []
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(validate_single_diagram, diagram): diagram
            for diagram in diagrams
        }

        for future in as_completed(futures):
            diagram, is_valid, error = future.result()
            if not is_valid:
                failed.append((diagram, error))

    return diagrams, failed


def main():
    parser = argparse.ArgumentParser(
        description="Extract and validate Mermaid diagrams from Markdown files"
    )
    parser.add_argument(
        "markdown_file",
        help="Path to the markdown file containing Mermaid diagrams"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Number of parallel workers for validation (default: 4)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only output errors, suppress success messages"
    )

    args = parser.parse_args()

    # Check if file exists
    markdown_path = Path(args.markdown_file)
    if not markdown_path.exists():
        print(f"✗ File not found: {args.markdown_file}", file=sys.stderr)
        sys.exit(3)

    # Validate all diagrams
    diagrams, failed = validate_markdown_file(markdown_path, args.workers)

    if not diagrams:
        if not args.quiet:
            print("No Mermaid diagrams found in the file.")
        sys.exit(0)

    # Report results
    if not args.quiet:
        print(f"Found {len(diagrams)} Mermaid diagram(s)")

    if not failed:
        if not args.quiet:
            print("✓ All diagrams are valid")
        sys.exit(0)
    else:
        print(f"✗ {len(failed)} diagram(s) have syntax errors:", file=sys.stderr)
        for diagram, error in failed:
            print(f"\nDiagram #{diagram.index} (lines {diagram.start_line}-{diagram.end_line}):", file=sys.stderr)
            print(f"  Error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
