# Sudoku Extractor

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/Izayoi-Tsuki/sudoku-extractor)](https://github.com/Izayoi-Tsuki/sudoku-extractor)

A Python-based tool that extracts digits from sudoku puzzle images and exports them to Excel format. Uses EasyOCR for optical character recognition and OpenCV for image processing.

![Sudoku Extractor Demo](https://via.placeholder.com/600x200?text=Sudoku+Extractor+Demo)

## ✨ Features

- 🔍 **Automatic Grid Detection** - Detects and splits 9x9 sudoku grids from images
- 📝 **OCR Recognition** - Uses EasyOCR for digit recognition (pure Python, no external dependencies)
- 📊 **Excel Export** - Outputs results with metadata to `.xlsx` files
- 📁 **Batch Processing** - Process multiple images at once
- 🖥️ **GUI Interface** - Simple Tkinter-based graphical interface
- 🔧 **Debug Mode** - Save intermediate processing images for troubleshooting

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Izayoi-Tsuki/sudoku-extractor.git
cd sudoku-extractor

# Create virtual environment (optional but recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### Command Line

```bash
# Process a single image
python src/main.py path/to/sudoku.png

# Process with debug mode (saves intermediate images)
python src/main.py path/to/sudoku.png -d

# Batch process all images in a directory
python src/main.py path/to/images/ --batch

# Specify output file
python src/main.py sudoku.png -o output.xlsx

# Show help
python src/main.py --help
```

#### GUI

```bash
# Run the graphical interface
python src/main.py
```

## 📖 Documentation

### Input Requirements

For best results, your sudoku images should:

- ✅ Be clear and well-lit
- ✅ Have the grid fully visible
- ✅ Be relatively straight (not tilted)
- ✅ Have good contrast between numbers and background

### Output Format

The program outputs an Excel file (`.xlsx`) with:
- **Source filename** - The original image name
- **Timestamp** - When the extraction was performed
- **9x9 Grid** - The recognized sudoku digits
- Empty cells are represented as blank or `.`

Example output:
```
Source File: sudoku_test.png
Extracted At: 2026-02-02 12:00:00

5  3  .  .  7  .  .  .  .
8  .  .  .  9  5  .  .  .
.  9  8  .  .  .  .  8  .
8  .  .  .  6  .  .  .  3
.  .  .  8  .  3  .  .  .
7  .  .  .  2  .  .  .  6
.  8  .  .  .  .  2  8  .
.  .  .  4  1  9  .  .  5
.  .  .  .  8  .  .  7  9
```

## 🏗️ Project Structure

```
sudoku-extractor/
├── src/                    # Source code
│   ├── main.py            # Main entry point & CLI
│   ├── image_processor.py  # Image preprocessing
│   ├── grid_detector.py    # Grid detection & splitting
│   ├── ocr_engine.py       # OCR digit recognition
│   ├── excel_writer.py     # Excel export
│   └── gui.py             # Tkinter GUI
├── test-input/             # Test images
├── test-output/            # Debug output directory
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Module Details

| Module | Description |
|--------|-------------|
| `main.py` | Entry point with CLI argument parsing |
| `image_processor.py` | Grayscale conversion, thresholding, contrast enhancement |
| `grid_detector.py` | Finds grid boundaries, splits into 81 cells |
| `ocr_engine.py` | Uses EasyOCR to recognize digits in each cell |
| `excel_writer.py` | Writes results to Excel with metadata |
| `gui.py` | Simple Tkinter interface for easy use |

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |

### CLI Options

```
usage: main.py [-h] [-o OUTPUT] [-d] [--batch] [image]

Extract digits from sudoku images to Excel

positional arguments:
  image                 Input image path or directory

options:
  -h, --help           Show this help message
  -o OUTPUT, --output OUTPUT
                       Output file path or directory
  -d, --debug          Enable debug mode (save intermediate images)
  --batch              Batch processing mode (when input is directory)
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| Recognition Rate | ~70-80% on clear images |
| Processing Time | ~10-20 seconds per image |
| Supported Formats | PNG, JPG, JPEG, BMP, TIFF |

### Factors Affecting Accuracy

- 📷 **Image clarity** - Blurry images reduce accuracy
- 💡 **Lighting** - Uneven lighting causes issues
- 📐 **Grid alignment** - Tilted grids may not detect properly
- ✍️ **Digit style** - Handwritten digits are harder to recognize than printed

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - Pure Python OCR library with 80+ language support
- [OpenCV](https://opencv.org/) - Industry-standard computer vision library
- [Pillow](https://python-pillow.org/) - Python Imaging Library
- [openpyxl](https://openpyxl.readthedocs.io/) - Python library to read/write Excel files

## 📧 Contact

- GitHub: [@Izayoi-Tsuki](https://github.com/Izayoi-Tsuki)
- Repository: https://github.com/Izayoi-Tsuki/sudoku-extractor

---

⭐ Star this repo if you find it useful!
