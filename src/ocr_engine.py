"""
OCR Engine Module
Use EasyOCR for local digit recognition with enhanced preprocessing
"""

import cv2
import numpy as np
from typing import Optional, List
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


class OCREngine:
    """Sudoku digit OCR engine using EasyOCR with enhanced preprocessing"""
    
    def __init__(self, lang: str = 'en'):
        """
        Initialize OCR engine
        
        Args:
            lang: Language ('en' for English digits)
        """
        self.lang = lang
        self.reader = None
        self._load_engine()
    
    def _load_engine(self):
        """Load EasyOCR reader"""
        try:
            import easyocr
            # Use GPU=False for CPU-only
            self.reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            print("[OK] EasyOCR engine loaded")
        except Exception as e:
            print(f"[FAIL] EasyOCR load failed: {e}")
            raise
    
    def preprocess_cell(self, cell: np.ndarray) -> np.ndarray:
        """
        Enhanced preprocessing for cell image
        
        Args:
            cell: Cell numpy array
            
        Returns:
            Preprocessed numpy array
        """
        # Convert to grayscale if needed
        if len(cell.shape) == 3:
            gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)
        else:
            gray = cell.copy()
        
        # Ensure minimum size (EasyOCR needs enough pixels)
        min_size = 45
        h, w = gray.shape
        if h < min_size or w < min_size:
            scale = min_size / max(h, w)
            new_size = (int(w * scale), int(h * scale))
            gray = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)
        
        # Invert if most pixels are white (text should be black on white)
        if np.mean(gray) > 127:
            gray = 255 - gray
        
        # Increase contrast using CLAHE
        try:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            gray = clahe.apply(gray)
        except:
            gray = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        
        # Light denoising
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Otsu thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def extract_digit(self, cell: np.ndarray) -> Optional[str]:
        """
        Extract digit from cell with enhanced preprocessing
        
        Args:
            cell: Cell image
            
        Returns:
            Digit string or None
        """
        try:
            # Enhanced preprocessing
            img = self.preprocess_cell(cell)
            
            # EasyOCR recognition
            results = self.reader.readtext(img, detail=1)
            
            if not results:
                return None
            
            # Find the best digit result
            best_digit = None
            best_confidence = 0
            
            for result in results:
                if len(result) >= 2:
                    text = result[1]
                    confidence = result[2] if len(result) > 2 else 1.0
                    
                    # Extract only digits
                    digit = ''.join(c for c in str(text) if c.isdigit())
                    
                    # Filter out multi-digit results
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
                                       empty_threshold: float = 0.85) -> List[str]:
        """
        Extract grid with enhanced empty cell detection
        
        Args:
            cells: 81 cell images
            empty_threshold: White pixel ratio threshold
            
        Returns:
            List of 81 digits or empty strings
        """
        results = []
        for i, cell in enumerate(cells):
            # Enhanced empty cell check
            if self._is_empty_cell(cell, empty_threshold):
                results.append('')
                continue
            
            digit = self.extract_digit(cell)
            results.append(digit if digit else '')
        
        return results
    
    def _is_empty_cell(self, cell: np.ndarray, threshold: float = 0.90) -> bool:
        """
        Simple empty cell detection (回滚到简单版本)
        
        Args:
            cell: Cell image
            threshold: White pixel ratio threshold
            
        Returns:
            True if empty
        """
        if len(cell.shape) == 3:
            gray = np.mean(cell, axis=2)
        else:
            gray = cell
        
        # 检查白色像素比例
        white_pixels = np.sum(gray > 200)
        total_pixels = gray.size
        white_ratio = white_pixels / total_pixels
        
        # 降低阈值，更宽松地判断为空
        if white_ratio > 0.93:
            return True
        
        return False


if __name__ == "__main__":
    engine = OCREngine()
    print("\n[USAGE]")
    print("   - extract_digit(): Recognize single cell")
    print("   - extract_grid(): Recognize all 81 cells")
    print("   - extract_grid_with_empty_check(): With empty detection")
