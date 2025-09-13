#!/usr/bin/env python3
"""
Command-line interface for PDF → PNG conversion using logic.py
cli.py <files-or-folders> --dpi 600 --alpha --overwrite --password "secret"
"""

from typing import List
import argparse

# Import the core logic
import logic


def _main() -> int:
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Convert PDFs to PNG images beside the source files."
    )

    # Positional arguments
    parser.add_argument(
        "inputs",
        nargs="+",
        help="PDF files and/or folders (folders searched recursively).",
    )

    # --- Optional arguments ---

    parser.add_argument(
        "--dpi",
        type=int,
        default=600,
        help="Render resolution in DPI (default: 600).",
    )

    parser.add_argument(
        "--alpha",
        action="store_true",
        help="Keep transparency (alpha channel).",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing PNG files.",
    )

    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Password to open encrypted PDFs (applies to all).",
    )

    # Parse the args
    args = parser.parse_args()

    # Find PDFs from inputs
    pdfs = logic.find_pdfs(args.inputs)

    # Report if none found
    if not pdfs:
        print("[INFO] No PDFs found.")
        return 1

    # Convert each PDF
    for pdf in pdfs:
        logic.convert_pdf(
            pdf,
            dpi=args.dpi,
            overwrite=args.overwrite,
            alpha=args.alpha,
            password=args.password,
            log=None,
        )
    
    return 0

# Entry point
if __name__ == "__main__":
    # Exit with the return code from _main()
    # return 1 -> no PDFs found (non-zero exit for scripts)
    # return 0 -> success
    raise SystemExit(_main())