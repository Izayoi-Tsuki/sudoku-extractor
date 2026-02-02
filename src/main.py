"""
Sudoku Extractor - Main Entry
Extract digits from sudoku images to Excel
Using adaptive preprocessing + AI-powered OCR
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from image_processor import ImagePreprocessor
from grid_detector import GridDetector
from ocr_engine import OCREngine
from excel_writer import ExcelWriter
from typing import Optional
import cv2
import numpy as np


class SudokuExtractor:
    """Sudoku Extractor Main Class"""
    
    def __init__(self, debug: bool = False):
        """
        Initialize extractor
        
        Args:
            debug: Enable debug mode
        """
        self.debug = debug
        self.preprocessor = ImagePreprocessor(threshold=128)
        self.detector = GridDetector(debug=debug)
        self.ocr = OCREngine()
        self.writer = ExcelWriter()
        
        # New: Adaptive preprocessing parameters
        self.blur_size = (5, 5)
        self.adaptive_block = 51
        self.adaptive_c = 10
    
    def process(self, image_path: str, output_path: Optional[str] = None) -> list:
        """
        Process sudoku image
        
        Args:
            image_path: Input image path
            output_path: Output Excel path (optional)
            
        Returns:
            List of 81 digits
        """
        print(f"\n[PROCESSING] {image_path}")
        
        # 1. Load and enhance image
        print("   [1/5] Loading and enhancing image...")
        # Use PIL to handle non-ASCII paths
        from PIL import Image
        try:
            pil_img = Image.open(image_path)
            arr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise ValueError(f"Cannot load image: {image_path}")
        
        # Convert to grayscale
        if len(arr.shape) == 3:
            gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
        else:
            gray = arr.copy()
        
        # Resize if too small (minimum 300px)
        min_size = 300
        h, w = gray.shape
        if min(h, w) < min_size:
            scale = min_size / min(h, w)
            new_size = (int(w * scale), int(h * scale))
            gray = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)
        
        if self.debug:
            cv2.imwrite("debug_loaded.png", gray)
        
        # 2. Adaptive preprocessing (better than fixed threshold)
        print("   [2/5] Adaptive preprocessing...")
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, self.blur_size, 0)
        
        # Use Otsu's thresholding
        _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Invert for black text on white
        binary = 255 - otsu
        
        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        if self.debug:
            cv2.imwrite("debug_preprocessed.png", binary)
        
        # 3. Detect and split grid
        print("   [3/5] Detecting and splitting 9x9 grid...")
        cells = self.detector.detect_and_split(binary)
        print(f"       Split {len(cells)} cells successfully")
        
        # 4. OCR recognition with enhanced preprocessing
        print("   [4/5] Recognizing digits...")
        grid = self.ocr.extract_grid_with_empty_check(cells)
        
        # Display preview
        self._display_grid_preview(grid)
        
        # 5. Output to Excel
        print("   [5/5] Writing to Excel...")
        filename = output_path or f"{Path(image_path).stem}_sudoku.xlsx"
        self.writer.write_with_metadata(grid, Path(image_path).name, filename)
        
        return grid
    
    def _display_grid_preview(self, grid: list):
        """Display grid preview"""
        print("\n   [PREVIEW] Recognition result:")
        print("   " + "-" * 25)
        for row in range(9):
            row_data = []
            for col in range(9):
                val = grid[row * 9 + col]
                row_data.append(val if val else ".")
            # Add separators every 3 columns
            formatted = "  ".join([
                "  ".join(row_data[i:i+3]) 
                for i in range(0, 9, 3)
            ])
            print(f"   | {formatted} |")
        print("   " + "-" * 25)
        print()
    
    def batch_process(self, image_dir: str, output_dir: Optional[str] = None):
        """
        Batch process images
        
        Args:
            image_dir: Image directory
            output_dir: Output directory
        """
        from pathlib import Path
        import os
        
        image_path = Path(image_dir)
        output_path = Path(output_dir) if output_dir else image_path
        
        # Supported image formats
        extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
        image_files = [
            f for f in image_path.iterdir() 
            if f.suffix.lower() in extensions
        ]
        
        if not image_files:
            print(f"[ERROR] No images found in {image_dir}")
            return
        
        print(f"\n[BATCH] Found {len(image_files)} images\n")
        
        for i, img_file in enumerate(image_files, 1):
            print(f"{'─' * 50}")
            print(f"[{i}/{len(image_files)}]")
            try:
                self.process(str(img_file))
            except Exception as e:
                print(f"   [FAIL] Processing failed: {e}")
        
        print(f"\n{'─' * 50}")
        print(f"[SUCCESS] Batch processing complete")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract digits from sudoku images to Excel"
    )
    parser.add_argument(
        "image", 
        nargs="?", 
        help="Input image path or directory"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path or directory"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode (save intermediate images)"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch processing mode (when input is directory)"
    )
    
    args = parser.parse_args()
    
    if not args.image:
        parser.print_help()
        print("\n[USAGE EXAMPLES]")
        print("   python main.py sudoku.png")
        print("   python main.py sudoku.png -o output.xlsx")
        print("   python main.py ./images/ --batch")
        return
    
    # Check if file/directory exists
    if not os.path.exists(args.image):
        print(f"[ERROR] Path not found: {args.image}")
        return
    
    # Initialize extractor
    extractor = SudokuExtractor(debug=args.debug)
    
    # Process
    if os.path.isdir(args.image) and args.batch:
        extractor.batch_process(args.image, args.output)
    elif os.path.isdir(args.image):
        print(f"[WARNING] {args.image} is a directory")
        print("   Use --batch for batch processing")
    else:
        extractor.process(args.image, args.output)


if __name__ == "__main__":
    main()
