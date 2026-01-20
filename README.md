# AnalyseSI Modern

A modern MERISE database modeling tool built with Python and PySide6.

## Features

- **MCD Editor** - Visual diagram editor for entities, associations, and links
- **Data Dictionary** - Overview of all attributes across entities
- **MLD View** - Logical Data Model with table/column tree view
- **SQL Generation** - PostgreSQL CREATE TABLE statements
- **Project Management** - Save/load projects (.asip format)

## Screenshots

*(Add screenshots here)*

## Requirements

- Python 3.11+
- PySide6

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/AchrafSoltani/AnalyseSI.git
cd AnalyseSI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Pre-built Binaries

Download the latest release from the [Releases](https://github.com/AchrafSoltani/AnalyseSI/releases) page.

## Building from Source

### Prerequisites

```bash
pip install pyinstaller
```

### Build Commands

**Linux:**
```bash
# Activate virtual environment
source venv/bin/activate

# Build
python build.py build

# Output: dist/AnalyseSI (65 MB standalone executable)
```

**Windows:**
```bash
# Activate virtual environment
venv\Scripts\activate

# Create .ico from SVG (requires ImageMagick)
python build.py ico

# Build
python build.py build

# Output: dist\AnalyseSI.exe
```

**Clean build files:**
```bash
python build.py clean
```

## Distribution

### Linux

```bash
# Create a tarball with all necessary files
mkdir -p AnalyseSI-linux
cp dist/AnalyseSI AnalyseSI-linux/
cp resources/icons/app_icon.svg AnalyseSI-linux/
cp analysesi.desktop AnalyseSI-linux/
tar -czvf AnalyseSI-1.0.0-linux-x64.tar.gz AnalyseSI-linux
```

Users can then:
1. Extract the archive
2. Run `./AnalyseSI`
3. Optionally install the .desktop file for system integration

### Windows

```bash
# Create a ZIP archive
# Or use NSIS/Inno Setup for an installer
```

## Usage

1. **Create Entities** - Click "Add Entity" in the MCD tab, define name and attributes
2. **Create Associations** - Click "Add Association" to define relationships
3. **Link Them** - Click "Add Link" to connect entities to associations with cardinalities
4. **View MLD** - Switch to MLD tab to see the logical model
5. **Generate SQL** - Switch to SQL tab to see PostgreSQL DDL statements
6. **Save Project** - File > Save to save your work

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New Project |
| Ctrl+O | Open Project |
| Ctrl+S | Save Project |
| Ctrl+1 | Dictionary Tab |
| Ctrl+2 | MCD Tab |
| Ctrl+3 | MLD Tab |
| Ctrl+4 | SQL Tab |
| Delete | Delete Selected |
| Ctrl+Scroll | Zoom In/Out |

## Project Structure

```
AnalyseSI/
├── main.py                 # Application entry point
├── build.py                # Build script
├── analysesi.spec          # PyInstaller configuration
├── requirements.txt        # Python dependencies
├── resources/
│   └── icons/
│       └── app_icon.svg    # Application icon
├── src/
│   ├── models/             # Data models
│   ├── views/              # UI components
│   ├── controllers/        # Business logic
│   └── utils/              # Utilities and constants
└── tests/                  # Unit tests
```

## License

GNU GPL v2

## Author

Achraf SOLTANI

## Acknowledgments

Based on the original [AnalyseSI](https://launchpad.net/analysesi) Java project.
