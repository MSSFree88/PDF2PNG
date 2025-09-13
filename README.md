# PDF → PNG Converter

A lightweight toolset for batch converting **PDFs to PNG images** using [PyMuPDF](https://pymupdf.readthedocs.io/).  
Includes both a **command-line interface (CLI)** and a **drag-and-drop GUI**.

---

## ✨ Features

### CLI (`cli.py`)
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

## 📂 Project Structure
- `logic.py` - Core conversion logic (library functions)
- `cli.py` - Command-line interface (argument parsing + entry point)
- `gui.py` - Drag-and-drop GUI (tkinter + tkinterdnd2)

---

## ⚙️ Requirements
- Python **3.9+**
- **PyMuPDF**
- **Tkinter** (included with most Python installations)
- **tkinterdnd2** *(GUI Only)*
- **PyInstaller** (only if building executables)

---

## 🚀 Usage (Source)

### CLI
```bash
python cli.py [OPTIONS] INPUT [INPUT ...]
python cli.py INPUT [INPUT ...] [OPTIONS]
```
#### OPTIONS
- `--dpi <INT>` - Render resolution in DPI. (default: 600)
- `--alpha` - Keep transparency (alpha channel). (default: Off)
- `--overwrite` - Overwrite existing PNG files without prompting. (default: Off)
- `--password <STRING>` - Password to open encrypted PDFs (applies to all inputs). (default: None)

#### Example
```bash
# Basic usage
python cli.py input.pdf

# Recursive folder search with custom options
python cli.py ~/Documents --dpi 300 --alpha --overwrite
```

### GUI
```bash
python gui.py
```
Then drag and drop PDFs/folders into the window, or use the buttons.

---

## 📥 Downloads (Executables)
If you just want to run it on Windows, download the .exe files from the `dist` folder

**Run the executable**
- **GUI:** Double-click PDF2PNG.exe
- **CLI:** Open Terminal in the folder and run:
```bash
"PDF2PNG CLI.exe" INPUT [INPUT ...] [OPTIONS]
```

---

## 🛠️ Build & Run (Executable)

### Build GUI version
```bash
pyinstaller gui.py --name "PDF2PNG" --noconsole --onefile --collect-all tkinterdnd2 --collect-all pymupdf --icon ./icon/icon.ico
```

### Build CLI version
```bash
pyinstaller cli.py --name "PDF2PNG CLI" --onefile --collect-all tkinterdnd2 --collect-all pymupdf --icon ./icon/icon.ico
```

---

## 🔮 Future Improvements
- Optional threading in GUI for large jobs (to keep UI responsive).
- Configurable output naming patterns.
- Option to merge results into a single image strip.
