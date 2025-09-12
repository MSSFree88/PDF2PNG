#!/usr/bin/env python3
"""
Core logic for converting PDFs to PNGs using PyMuPDF.

Public API:
- find_pdfs(inputs: Iterable[str]) -> list[Path]
- convert_pdf(pdf_path: Path, *, dpi: int, overwrite: bool, alpha: bool,
              password: str | None, log: Callable[[str], None] | None = None) -> None
"""

from __future__ import annotations
from pathlib import Path
from typing import Iterable, Callable
import pymupdf


# ---------------- Utilities ----------------

# Write a message to the provided logger or stdout.
def _say(msg: str, log: Callable[[str], None] | None) -> None:
    (log or print)(msg)

# Return a de-duplicated list of PDF paths from files/folders (folders searched recursively).
def find_pdfs(inputs: Iterable[str]) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []

    for raw in inputs:
        p = Path(raw).expanduser().resolve()
        
        # Check if it is a PDF
        if p.is_file() and p.suffix.lower() == ".pdf":
            if p not in seen:
                seen.add(p)
                out.append(p)
        
        # Check if it is a directory
        elif p.is_dir():
            # Recursively scan directory; filter by extension in a case-insensitive way
            for path in p.rglob("*.[Pp][Dd][Ff]"):
                path = path.resolve()
                if path not in seen:
                    seen.add(path)
                    out.append(path)

        # Silently ignore non-existent / non-PDF items

    return out


# ---------------- Conversion ----------------

# Convert one PDF to PNG(s) next to it.
def convert_pdf(
    pdf_path: Path,
    *, # '*' makes everything after it keyword-only: must call with dpi=..., overwrite=..., etc.
    dpi: int,
    overwrite: bool,
    alpha: bool,
    password: str | None,
    log: Callable[[str], None] | None = None,
) -> None:
    
    # Local logger
    def say(m: str) -> None: _say(m, log)

    # Try to open the PDF; if it fails (missing/corrupt/unsupported), log and stop
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        say(f"[ERROR] Could not open '{pdf_path.name}': {e}")
        return

    try:
        # Handle encryption (require and verify password if needed)
        if getattr(doc, "needs_pass", False):
            if not password or not doc.authenticate(password):
                say(f"[ERROR] Password required/failed for '{pdf_path.name}'. Skipping.")
                return

        # Check page count
        page_count = doc.page_count
        if page_count == 0:
            say(f"[WARN] '{pdf_path.name}' has 0 pages. Skipping.")
            return

        # Compute render scale: PDFs are 72 points/in; scale = requested_dpi / 72
        scale = max(dpi, 1) / 72.0 
        zoom = pymupdf.Matrix(scale, scale)

        # Prepare output paths
        stem = pdf_path.stem
        parent = pdf_path.parent

        # For single-page PDFs
        if page_count == 1:
            # Save single-page as "<name>.png" next to the PDF (path-join via pathlib "/")
            out_png = parent / f"{stem}.png"

            # Skip if exists and not overwriting
            if out_png.exists() and not overwrite:
                say(f"[SKIP] Exists (use --overwrite): {out_png}")
                return

            # Render and save
            try:
                page = doc.load_page(0)
                # Render page to bitmap; alpha=True keeps transparency (RGBA)
                pix = page.get_pixmap(matrix=zoom, alpha=alpha)
                pix.save(out_png)
            except Exception as e:
                say(f"[WARN] Failed to render/save '{pdf_path.name}' Pg 1: {e}")
                return
            
            say(f"[OK] {pdf_path.name} -> {out_png.name}")
            return

        # For multi-page PDFs, create output directory
        out_dir = parent / stem
        out_dir.mkdir(parents=True, exist_ok=True)

        # Convert each page
        # Multi-page -> "<name>/" with "<name> - Pg N.png"
        for i in range(page_count):
            out_png = out_dir / f"{stem} - Pg {i+1}.png"

            # Skip if exists and not overwriting
            if out_png.exists() and not overwrite:
                say(f"[SKIP] Exists (use --overwrite): {out_png}")
                continue

            # Render and save
            try:
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=zoom, alpha=alpha)
                pix.save(out_png)
            except Exception as e:
                say(f"[WARN] Failed to render/save '{pdf_path.name}' Pg {i+1}: {e}")
                continue

        say(f"[OK] {pdf_path.name} -> {out_dir}/(Pg 1..{page_count})")

    # Ensure the document is closed
    finally:
        # Always close the document (even on early return/exception)
        try: doc.close()
        except Exception: pass


# Entry (point for direct run, which we do not want)
if __name__ == "__main__":
    return_code = 1
    print("[ERROR] This module is not meant to be run directly. Use cli.py or gui.py.")
    exit(return_code)