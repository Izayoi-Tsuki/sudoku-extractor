"""
图像预处理模块
功能：读取、预处理数独图片（灰度化、二值化、去噪）
"""

from PIL import Image
import numpy as np
from typing import Tuple


class ImagePreprocessor:
    """数独图片预处理器"""
    
    def __init__(self, threshold: int = 128):
        """
        初始化预处理器
        
        Args:
            threshold: 二值化阈值 (0-255)
        """
        self.threshold = threshold
    
    def load(self, image_path: str) -> Image.Image:
        """
        加载图片
        
        Args:
            image_path: 图片路径
            
        Returns:
            PIL Image 对象
        """
        img = Image.open(image_path)
        return img
    
    def to_grayscale(self, img: Image.Image) -> Image.Image:
        """
        转换为灰度图
        
        Args:
            img: PIL Image 对象
            
        Returns:
            灰度图
        """
        if img.mode != 'L':
            img = img.convert('L')
        return img
    
    def binarize(self, img: Image.Image, invert: bool = False) -> Image.Image:
        """
        二值化处理
        
        Args:
            img: 灰度图
            invert: 是否反转（黑底转白底）
            
        Returns:
            二值化图 (白底黑字)
        """
        arr = np.array(img)
        binary = (arr > self.threshold).astype(np.uint8) * 255
        
        if invert:
            binary = 255 - binary
            
        return Image.fromarray(binary)
    
    def detect_background(self, img: Image.Image) -> bool:
        """
        检测背景颜色
        返回 True 表示白底，False 表示黑底
        
        Args:
            img: 灰度图
            
        Returns:
            是否为白底
        """
        arr = np.array(img)
        # 采样边缘像素判断背景
        edges = np.concatenate([
            arr[0, :],           # 上边缘
            arr[-1, :],          # 下边缘
            arr[:, 0],           # 左边缘
            arr[:, -1]           # 右边缘
        ])
        mean_bg = np.mean(edges)
        return mean_bg > 127  # 白色背景平均亮度高
    
    def enhance_contrast(self, img: Image.Image, factor: float = 1.5) -> Image.Image:
        """
        增加对比度
        
        Args:
            img: 灰度图
            factor: 对比度因子
            
        Returns:
            增强后的图
        """
        arr = np.array(img).astype(np.float64)
        # 线性变换
        mean = np.mean(arr)
        enhanced = (arr - mean) * factor + mean
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        return Image.fromarray(enhanced)
    
    def preprocess(self, image_path: str) -> Tuple[Image.Image, np.ndarray]:
        """
        完整的预处理流程
        
        Args:
            image_path: 图片路径
            
        Returns:
            (预处理后的图, numpy数组)
        """
        # 1. 加载
        img = self.load(image_path)
        
        # 2. 灰度化
        gray = self.to_grayscale(img)
        
        # 3. 检测背景并决定是否反转
        is_white_bg = self.detect_background(gray)
        
        # 4. 增强对比度
        enhanced = self.enhance_contrast(gray)
        
        # 5. 二值化（自动反转，确保白底黑字）
        binary = self.binarize(enhanced, invert=not is_white_bg)
        
        return binary, np.array(binary)


if __name__ == "__main__":
    # Test
    preprocessor = ImagePreprocessor(threshold=128)
    print("[OK] ImagePreprocessor loaded")
    print("   - load(): Load image")
    print("   - to_grayscale(): Convert to grayscale")
    print("   - binarize(): Binarize")
    print("   - enhance_contrast(): Enhance contrast")
    print("   - preprocess(): Full preprocessing pipeline")
