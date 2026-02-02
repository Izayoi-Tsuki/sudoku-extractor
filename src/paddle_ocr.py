"""
PaddleOCR Engine Module
Alternative OCR using PaddlePaddle
"""

import cv2
import numpy as np
from typing import Optional, List
import warnings

warnings.filterwarnings('ignore')


class PaddleOCREngine:
    """Sudoku digit OCR engine using PaddleOCR"""
    
    def __init__(self):
        """Initialize PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            # Use CPU only, no angle classification needed for digits
            self.reader = PaddleOCR(lang='en')
            print("[OK] PaddleOCR engine loaded")
        except Exception as e:
            print(f"[FAIL] PaddleOCR load failed: {e}")
            raise
    
    def extract_digit(self, cell: np.ndarray) -> Optional[str]:
        """
        Extract digit from cell
        
        Args:
            cell: Cell image
            
        Returns:
            Digit string or None
        """
        try:
            # PaddleOCR needs RGB image as numpy array
            if len(cell.shape) == 3:
                cell_rgb = cv2.cvtColor(cell, cv2.COLOR_BGR2RGB)
            else:
                cell_rgb = cv2.cvtColor(cell, cv2.COLOR_GRAY2RGB)
            
            # Run OCR directly on the image array
            result = self.reader.ocr(cell_rgb)
            
            if not result or not result[0]:
                return None
            
            # Extract digit from result
            best_digit = None
            best_confidence = 0
            
            for line in result[0]:
                if line:
                    text = line[1][0]  # Text
                    confidence = line[1][1]  # Confidence
                    
                    # Extract only digits
                    digit = ''.join(c for c in str(text) if c.isdigit())
                    
                    if digit and len(digit) == 1 and confidence > best_confidence:
                        best_digit = digit
                        best_confidence = confidence
            
            return best_digit
            
        except Exception as e:
            return None
    
    def extract_grid(self, cells: List[np.ndarray]) -> List[Optional[str]]:
        """
        Extract all 81 digits from grid
        
        Args:
            cells: List of 81 cell images
            
        Returns:
            List of 81 digits/None
        """
        results = []
        for i, cell in enumerate(cells):
            digit = self.extract_digit(cell)
            results.append(digit)
            if (i + 1) % 20 == 0:
                print(f"   Progress: {i + 1}/81")
        return results
    
    def extract_grid_with_empty_check(self, cells: List[np.ndarray],
                                       empty_threshold: float = 0.90) -> List[str]:
        """
        Extract grid with empty cell detection
        
        Args:
            cells: 81 cell images
            empty_threshold: White pixel ratio threshold
            
        Returns:
            List of 81 digits or empty strings
        """
        results = []
        for i, cell in enumerate(cells):
            if self._is_empty_cell(cell, empty_threshold):
                results.append('')
                continue
            digit = self.extract_digit(cell)
            results.append(digit if digit else '')
        return results
    
    def _is_empty_cell(self, cell: np.ndarray, threshold: float = 0.90) -> bool:
        """Check if cell is empty"""
        if len(cell.shape) == 3:
            gray = np.mean(cell, axis=2)
        else:
            gray = cell
        
        white_pixels = np.sum(gray > 200)
        total_pixels = gray.size
        white_ratio = white_pixels / total_pixels
        
        if white_ratio > 0.93:
            return True
        return False


if __name__ == "__main__":
    engine = PaddleOCREngine()
    print("\n[USAGE]")
    print("   - extract_digit(): Recognize single cell")
    print("   - extract_grid(): Recognize all 81 cells")
