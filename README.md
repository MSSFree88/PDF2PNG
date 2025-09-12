# PDF → PNG Converter

A lightweight toolset for batch converting **PDFs to PNG images** using [PyMuPDF](https://pymupdf.readthedocs.io/).  
Includes both a **command-line interface (CLI)** and a **drag-and-drop GUI**.

---

## ✨ Features

### CLI (`main.py`)
- Convert single PDFs or entire folders (recursive search).
- Handles single-page and multi-page PDFs  
  ↳ Multi-page outputs to a subfolder.
- Options for DPI, transparency (alpha), overwrite control, and password-protected files.

### GUI (`gui.py`)
- Drag & drop PDFs or folders (requires [`tkinterdnd2`](https://pypi.org/project/tkinterdnd2/)).
- Add/remove PDFs and folders via buttons.
- Scrollable target list with placeholder when empty.
- Configurable DPI, alpha channel, overwrite mode, and optional password input.
- Logs conversion progress in-window.

---

## 🚀 Usage

### CLI
```bash
# Basic usage
python main.py input.pdf

# Recursive folder search with custom options
python main.py ~/Documents --dpi 300 --alpha --overwrite
```

### GUI
```bash
python gui.py
```
Then drag and drop PDFs/folders into the window, or use the buttons.

---

## ⚙️ Requirements
- Python **3.9+**
- **PyMuPDF**
- **Tkinter** (included with most Python installations)
- **tkinterdnd2** *(GUI Only)*
- **PyInstaller** (only if building executables)

---

## 📂 Project Structure
```bash
main.py   # Core CLI converter logic
gui.py    # GUI wrapper for drag-and-drop
```

---

## 🔮 Future Improvements
- Optional threading in GUI for large jobs (to keep UI responsive).
- Configurable output naming patterns.
- Option to merge results into a single image strip.
