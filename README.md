# Sudoku Extractor

A Python-based tool that extracts digits from sudoku puzzle images and exports them to Excel format.

## Features

- **Automatic Grid Detection** - Detects and splits 9x9 sudoku grids from images
- **OCR Recognition** - Uses EasyOCR for digit recognition
- **Excel Export** - Outputs results with metadata to `.xlsx` files
- **Batch Processing** - Process multiple images at once
- **GUI Interface** - Simple Tkinter-based graphical interface

## Requirements

- Python 3.8+
- Windows/Linux/macOS
- EasyOCR
- OpenCV
- NumPy
- Pillow
- openpyxl

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sudoku-extractor.git
cd sudoku-extractor

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Process a single image
python src/main.py path/to/sudoku.png

# Process with debug mode (saves intermediate images)
python src/main.py path/to/sudoku.png -d

# Batch process all images in a directory
python src/main.py path/to/images/ --batch

# Specify output file
python src/main.py sudoku.png -o output.xlsx
```

### GUI

```bash
# Run the graphical interface
python src/main.py
# Or simply double-click the batch file if available
```

## Project Structure

```
sudoku-extractor/
├── src/                    # Source code
│   ├── main.py            # Main entry point
│   ├── image_processor.py  # Image preprocessing
│   ├── grid_detector.py    # Grid detection and splitting
│   ├── ocr_engine.py       # OCR digit recognition
│   └── excel_writer.py     # Excel export
├── test-input/             # Test images
├── test-output/            # Debug output directory
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## How It Works

1. **Image Preprocessing** - Converts to grayscale, applies adaptive thresholding
2. **Grid Detection** - Finds the sudoku grid boundaries
3. **Cell Splitting** - Divides the grid into 81 individual cells
4. **OCR Recognition** -识别每个单元格中的数字
5. **Export** - Writes results to Excel with timestamp and source filename

## Testing

Place test images in the `test-input/` directory and run:

```bash
python src/main.py test-input/ --batch
```

## Performance

- **Recognition Rate**: ~70-80% on clear, well-lit images
- **Processing Time**: ~10-20 seconds per image
- **Accuracy Factors**:
  - Image clarity and lighting
  - Grid alignment
  - Digit style (handwritten vs printed)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - Pure Python OCR library
- [OpenCV](https://opencv.org/) - Computer vision library
- [Pillow](https://python-pillow.org/) - Python Imaging Library
