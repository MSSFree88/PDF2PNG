#!/usr/bin/env python3
"""
GUI wrapper for pdf_to_png_core with drag-and-drop (tkinterdnd2 required).
- Drag PDFs/folders into the target area
- Add via buttons
- Scrollbars (vertical + horizontal)
- Placeholder shown until targets are added
"""

from __future__ import annotations
from pathlib import Path
from typing import List
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

# Core conversion module (adjust import if you renamed it)
import logic as core

# -------------------- Config --------------------
APP_TITLE = "PDF → PNG Converter"
DPI_CHOICES = ["72", "96", "144", "300", "600", "1200", "2400", "3600", "4800"]
DEFAULT_DPI = "600"
USE_MONO_LIST_FONT = False  # Set True if you prefer monospaced list display

# Optional placeholder image (PNG). Leave as None for text-only.
PLACEHOLDER_IMAGE: Path | None = None  # e.g., Path(__file__).with_name("dragdrop.png")


# -------------------- Helpers --------------------

# Split a DND_FILES payload into individual Path objects (handles braces & spaces).
def _split_dnd_paths(data: str) -> List[Path]:
    items: List[str] = []
    token, brace = "", 0
    
    # Loop through characters
    # TkinterDND2 uses braces to group paths with spaces in them
    for ch in data:
        # Handle opening brace
        if ch == "{":
            brace += 1

        # Handle closing brace
        elif ch == "}":
            brace = max(0, brace - 1)
        
        # Handle spaces (only if not in braces)
        elif ch == " " and brace == 0:
            # If we have a token, save it
            if token:
                items.append(token)
                token = ""
        
        # Regular character
        else:
            token += ch
    
    # Final token
    if token:
        items.append(token)
    
    return [Path(s.strip()).expanduser().resolve() for s in items if s.strip()]


# -------------------- App --------------------
class App(TkinterDnD.Tk):
    # GUI constructor
    def __init__(self, initial_targets: List[Path]):
        # Initialize parent class
        super().__init__()

        # Window setup
        self.title(APP_TITLE)
        self.minsize(720, 480)

        # State
        self.targets: List[Path] = initial_targets[:]
        self.dpi_var = tk.StringVar(value=DEFAULT_DPI)
        self.alpha_var = tk.BooleanVar(value=True)
        self.overwrite_var = tk.BooleanVar(value=False)
        self.password_var = tk.StringVar(value="")
        self._ph_img_ref = None  # Needs persistent reference

        # Build UI
        self._build_ui()

        # Populates listbox
        self._refresh_targets()

        # Key bindings
        self._bind_keys()

    # ---------- UI ----------
    def _build_ui(self):
        pad = 10

        # Top (targets area)
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=pad, pady=(pad, 5))

        ttk.Label(top, text="Target PDFs / Folders (folders searched recursively):").pack(anchor="w")

        # Stack: list area + placeholder overlay
        stack = ttk.Frame(top)
        stack.pack(fill=tk.BOTH, expand=True)

        # List frame with scrollbars
        list_frame = ttk.Frame(stack)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        vscroll = ttk.Scrollbar(list_frame, orient="vertical")
        hscroll = ttk.Scrollbar(list_frame, orient="horizontal")

        # Listbox that supports multiple selection
        self.listbox = tk.Listbox(
            list_frame,
            height=10,
            selectmode=tk.EXTENDED,
            yscrollcommand=vscroll.set,
            xscrollcommand=hscroll.set,
            font=("Consolas", 10) if USE_MONO_LIST_FONT else None,
        )

        # Placement of list + scrollbars
        self.listbox.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Wire scrollbars to listbox view handlers
        vscroll.config(command=self.listbox.yview)
        hscroll.config(command=self.listbox.xview)

        # DnD onto list
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind("<<Drop>>", self._on_drop_files)

        # Placeholder overlay
        if PLACEHOLDER_IMAGE and PLACEHOLDER_IMAGE.exists():
            self._ph_img_ref = tk.PhotoImage(file=str(PLACEHOLDER_IMAGE))
            self.placeholder = ttk.Label(list_frame, image=self._ph_img_ref, anchor="center")
        else:
            self.placeholder = ttk.Label(
                list_frame,
                text="Drop PDFs or Folders Here",
                style="Placeholder.TLabel",
                anchor="center",
                justify="center",
                borderwidth=2,
                relief="groove",
            )

        # Placeholder positioning
        self.placeholder.place(relx=0, rely=0, relwidth=1, relheight=1)

        # DnD onto placeholder + click to open file picker
        self.placeholder.drop_target_register(DND_FILES)
        self.placeholder.dnd_bind("<<Drop>>", self._on_drop_files)
        self.placeholder.bind("<Button-1>", lambda e: self._add_pdfs())  # click to open picker

        # Middle row of buttons
        btns = ttk.Frame(top)
        btns.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btns, text="Add PDFs…", command=self._add_pdfs).pack(side=tk.LEFT)
        ttk.Button(btns, text="Add Folder…", command=self._add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Remove Selected", command=self._remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Clear All", command=self._clear_all).pack(side=tk.LEFT, padx=5)

        # Placeholder style
        style = ttk.Style(self)
        style.configure("Placeholder.TLabel", foreground="#7a7a7a", font=("Segoe UI", 12))

        # Options
        opts = ttk.LabelFrame(self, text="Options")
        opts.pack(side=tk.TOP, fill=tk.X, padx=pad, pady=5)

        # DPI dropdown
        ttk.Label(opts, text="DPI:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        dpi_combo = ttk.Combobox(opts, textvariable=self.dpi_var, values=DPI_CHOICES, state="readonly", width=8)
        dpi_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Checkbuttons (alpha & overwrite)
        ttk.Checkbutton(opts, text="Keep transparency (alpha)", variable=self.alpha_var).grid(row=0, column=2, sticky="w", padx=15)
        ttk.Checkbutton(opts, text="Overwrite existing PNGs", variable=self.overwrite_var).grid(row=0, column=3, sticky="w", padx=15)

        # Password entry field
        ttk.Label(opts, text="Password (optional):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(opts, textvariable=self.password_var, width=30, show="•").grid(row=1, column=1, sticky="w", padx=5, pady=5, columnspan=3)

        # Bottom (log + actions)
        bottom = ttk.Frame(self)
        bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=pad, pady=(5, pad))
        bottom.rowconfigure(0, weight=1)
        bottom.columnconfigure(0, weight=1)

        # Log text area (read-only)
        self.logbox = tk.Text(bottom, height=10, wrap="word", state="disabled")
        self.logbox.grid(row=0, column=0, sticky="nsew")

        # Bottom row of buttons
        actions = ttk.Frame(bottom)
        actions.grid(row=1, column=0, sticky="e", pady=(5, 0))
        ttk.Button(actions, text="Quit", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions, text="Start", command=self._start).pack(side=tk.RIGHT)

    # ---------- Key bindings ----------
    def _bind_keys(self):
        self.bind("<Control-o>", lambda e: self._add_pdfs())
        self.bind("<Delete>", lambda e: self._remove_selected())
        self.bind("<Control-l>", lambda e: self._clear_all())
        self.bind("<Return>", lambda e: self._start())

    # ---------- DnD ----------
    def _on_drop_files(self, event):
        # Track if we added anything
        added = False

        # Split and add each path
        for p in _split_dnd_paths(event.data):
            # Only add if it exists and is not already in the list
            if p.exists() and p not in self.targets:
                self.targets.append(p)
                added = True
        
        # Refresh the list if we added anything
        if added:
            self._refresh_targets()

    # ---------- Target list helpers ----------

    # Refresh the listbox from self.targets
    def _refresh_targets(self):
        # Clear and re-populate
        self.listbox.delete(0, tk.END)

        # Append each target to the listbox
        for p in self.targets:
            self.listbox.insert(tk.END, str(p))

        # Show/Hide placeholder
        if self.targets:
            self.placeholder.place_forget()
        else:
            self.placeholder.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Add PDFs via file dialog
    def _add_pdfs(self):
        # Show file dialog to select PDFs
        paths = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF files", "*.pdf")])

        # Abort if user cancelled
        if not paths:
            return
        
        # Loop over selected paths
        for s in paths:
            p = Path(s).expanduser().resolve()
            
            # Only add if it is a PDF and not already in the list
            if p.is_file() and p.suffix.lower() == ".pdf" and p not in self.targets:
                self.targets.append(p)
        
        # Refresh the list
        self._refresh_targets()

    # Handler for "Add Folder" button
    def _add_folder(self):
        # Show folder picker dialog
        folder = filedialog.askdirectory(title="Select folder containing PDFs")
        
        # Abort if user cancelled
        if not folder:
            return
        
        p = Path(folder).expanduser().resolve()

        # Only add if it is a directory and not already in the list
        if p.is_dir() and p not in self.targets:
            self.targets.append(p)

        # Refresh the list
        self._refresh_targets()

    # Remove selected items from the list
    def _remove_selected(self):
        # Remove in reverse order to avoid messing up indices
        for idx in reversed(self.listbox.curselection()):
            # Remove the corresponding target
            del self.targets[idx]

        # Refresh the list
        self._refresh_targets()

    # Handler for "Clear All" button
    def _clear_all(self):
        # Clear targets from list
        self.targets.clear()

        # Refresh the list
        self._refresh_targets()

    # Log messages to the logbox
    def log(self, msg: str):
        # Enable editing
        self.logbox.configure(state="normal")

        # Append message
        self.logbox.insert(tk.END, msg + "\n")

        # Scroll to end
        self.logbox.see(tk.END)

        # Disable editing
        self.logbox.configure(state="disabled")

        # Update UI
        self.update_idletasks()

    # ---------- Convert ----------
    # Handler for "Start" button
    #
    # NOTE: Currently runs conversion synchronously on the main GUI thread.
    # This is fine for small jobs, but the UI will freeze during long batches.
    #
    # If you ever want responsiveness during large jobs:
    #   - Move the loop into a worker thread
    #   - Send log messages back via queue + self.after()
    #   - Disable controls while the worker is running
    def _start(self):
        # Check we have targets
        if not self.targets:
            messagebox.showwarning("No targets", "Please add at least one PDF or folder.")
            return
        
        # Validate DPI
        try:
            dpi = int(self.dpi_var.get())
        except ValueError:
            messagebox.showerror("Invalid DPI", f"Invalid DPI value: {self.dpi_var.get()}")
            return

        # Get other options
        alpha = bool(self.alpha_var.get())
        overwrite = bool(self.overwrite_var.get())
        password = self.password_var.get().strip() or None

        # Find all PDFs from targets
        all_pdfs = core.find_pdfs([str(p) for p in self.targets])
        
        # Abort if none found
        if not all_pdfs:
            messagebox.showinfo("No PDFs found", "No PDFs were found in the selected targets.")
            return

        # Log start message
        self.log(f"Found {len(all_pdfs)} PDF(s). Converting at {dpi} DPI…")
        
        # Loop through and convert each PDF
        for pdf in all_pdfs:
            # Log the PDF being processed and convert
            self.log(f"→ {pdf}")
            core.convert_pdf(pdf, dpi=dpi, overwrite=overwrite, alpha=alpha, password=password, log=self.log)
        
        self.log("Done ✅")


# -------------------- Entry --------------------
def main(argv: List[str]) -> int:
    initial: List[Path] = []
    
    # Process command-line args as initial targets
    for raw in argv:
        p = Path(raw).expanduser().resolve()
        
        # Only add if it exists and is not already in the list
        if p.exists() and p not in initial:
            initial.append(p)
    
    # Start the app
    App(initial).mainloop()
    
    return 0

# Entry point
if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))