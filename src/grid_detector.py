"""
网格检测模块
功能：检测并分割 9x9 数独网格
使用轮廓检测 + 透视变换 + 自适应分割
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List


class GridDetector:
    """数独网格检测器"""
    
    def __init__(self, grid_size: int = 9, debug: bool = False):
        """
        初始化网格检测器
        
        Args:
            grid_size: 网格大小 (默认9x9)
            debug: 是否输出调试信息
        """
        self.grid_size = grid_size
        self.debug = debug
    
    def find_contours(self, binary_img: np.ndarray) -> List[np.ndarray]:
        """
        查找图像中的轮廓
        
        Args:
            binary_img: 二值化图 (numpy数组)
            
        Returns:
            轮廓列表
        """
        # 查找轮廓
        contours, _ = cv2.findContours(
            binary_img, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
    
    def find_largest_contour(self, contours: List[np.ndarray]) -> np.ndarray:
        """
        找到最大的轮廓（应该是数独网格）
        
        Args:
            contours: 轮廓列表
            
        Returns:
            最大轮廓
        """
        if not contours:
            raise ValueError("未找到任何轮廓")
        
        # 按面积排序
        sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
        return sorted_contours[0]
    
    def order_points(self, pts: np.ndarray) -> np.ndarray:
        """
        将四个角点按顺时针排序：左上、右上、右下、左下
        
        Args:
            pts: 四个角点
            
        Returns:
            排序后的角点
        """
        rect = np.zeros((4, 2), dtype="float32")
        
        # 计算各点的和与差
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        
        # 左上角：和最小
        rect[0] = pts[np.argmin(s)]
        # 右下角：和最大
        rect[2] = pts[np.argmax(s)]
        # 右上角：差最小 (y - x)
        rect[1] = pts[np.argmin(diff)]
        # 左下角：差最大
        rect[3] = pts[np.argmax(diff)]
        
        return rect
    
    def get_warped_image(self, binary_img: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """
        对网格进行透视变换，获取正视图
        
        Args:
            binary_img: 二值化图
            contour: 网格轮廓
            
        Returns:
            透视变换后的图像 (正方形)
        """
        # 近似轮廓
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        if len(approx) != 4:
            # 如果不是四边形，尝试其他方法
            x, y, w, h = cv2.boundingRect(contour)
            approx = np.array([
                [[x, y]],
                [[x + w, y]],
                [[x + w, y + h]],
                [[x, y + h]]
            ], dtype=np.int32)
        
        # 排序角点
        rect = self.order_points(approx.reshape(4, 2))
        
        # 计算目标尺寸
        # 根据图像大小动态调整，每个单元格至少50像素
        h, w = binary_img.shape
        max_dim = max(w, h)
        cell_size = max(450, max_dim)  # 保证足够的分辨率
        dst = np.array([
            [0, 0],
            [cell_size - 1, 0],
            [cell_size - 1, cell_size - 1],
            [0, cell_size - 1]
        ], dtype="float32")
        
        # 透视变换
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(binary_img, M, (cell_size, cell_size))
        
        return warped
    
    def split_into_cells(self, warped: np.ndarray) -> List[np.ndarray]:
        """
        将网格分割成 9x9 个单元格（极小边距版）
        
        Args:
            warped: 透视变换后的网格图
            
        Returns:
            81个单元格的列表
        """
        cells = []
        h, w = warped.shape
        cell_size = h // 9  # 假设是正方形
        
        # 极小边距，只留1-2像素，避免切到1和7
        margin = 2
        
        for row in range(9):
            for col in range(9):
                # 计算每个单元格的坐标
                y1 = row * cell_size + margin
                y2 = (row + 1) * cell_size - margin
                x1 = col * cell_size + margin
                x2 = (col + 1) * cell_size - margin
                
                # 确保坐标有效
                if y1 >= y2 or x1 >= x2:
                    y1 = row * cell_size
                    y2 = (row + 1) * cell_size
                    x1 = col * cell_size
                    x2 = (col + 1) * cell_size
                
                cell = warped[y1:y2, x1:x2]
                
                # 放大到至少 45x45
                if cell.shape[0] < 45 or cell.shape[1] < 45:
                    cell = cv2.resize(cell, (45, 45), interpolation=cv2.INTER_CUBIC)
                
                cells.append(cell)
        
        return cells
    
    def find_grid_lines_hough(self, binary_img: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        使用霍夫变换检测网格线
        
        Args:
            binary_img: 二值化图
            
        Returns:
            (水平线位置数组, 垂直线位置数组)
        """
        # 边缘检测
        edges = cv2.Canny(binary_img, 50, 150, apertureSize=3)
        
        # 检测水平线
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (int(binary_img.shape[1]/3), 1))
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        
        # 检测垂直线
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(binary_img.shape[0]/3)))
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        
        # 使用霍夫变换检测直线
        horizontal_pos = []
        vertical_pos = []
        
        # 简化：直接使用边缘检测找到线条位置
        # 水平线：检测每行的边缘密度
        h_lines = []
        for y in range(0, binary_img.shape[0], 5):
            row = edges[y, :]
            if np.sum(row > 0) > binary_img.shape[1] * 0.3:  # 至少有30%的边缘
                h_lines.append(y)
        
        # 聚类找到主要的水平线
        if h_lines:
            # 找到最可能的9条水平线（网格线）
            step = binary_img.shape[0] // 9
            for i in range(9):
                y_center = i * step
                # 找最近的检测到的线
                closest = min(h_lines, key=lambda x: abs(x - y_center))
                horizontal_pos.append(closest)
        
        # 垂直线类似处理
        v_lines = []
        for x in range(0, binary_img.shape[1], 5):
            col = edges[:, x]
            if np.sum(col > 0) > binary_img.shape[0] * 0.3:
                v_lines.append(x)
        
        if v_lines:
            step = binary_img.shape[1] // 9
            for i in range(9):
                x_center = i * step
                closest = min(v_lines, key=lambda x: abs(x - x_center))
                vertical_pos.append(closest)
        
        return np.array(horizontal_pos), np.array(vertical_pos)
    
    def detect_and_split(self, binary_img: np.ndarray) -> List[np.ndarray]:
        """
        检测网格并分割成单元格（改进版：优先均匀分割）
        
        Args:
            binary_img: 二值化图
            
        Returns:
            81个单元格的列表
        """
        h, w = binary_img.shape
        
        # 优先使用均匀分割（更可靠）
        # 确保是正方形
        size = max(h, w)
        
        # 创建正方形图像
        square = np.zeros((size, size), dtype=binary_img.dtype)
        
        # 计算偏移量
        y_offset = (size - h) // 2
        x_offset = (size - w) // 2
        
        # 复制图像到中心
        square[y_offset:y_offset + h, x_offset:x_offset + w] = binary_img
        
        # 分割成单元格
        cells = self.split_into_cells(square)
        
        return cells
    
    def _try_fallback_detection(self, binary_img: np.ndarray) -> np.ndarray:
        """
        备选检测方法：当找不到轮廓时使用全图
        
        Args:
            binary_img: 二值化图
            
        Returns:
            网格图像
        """
        h, w = binary_img.shape
        # 确保是正方形
        size = max(h, w)
        
        # 创建正方形图像
        square = np.zeros((size, size), dtype=binary_img.dtype)
        
        # 计算偏移量
        y_offset = (size - h) // 2
        x_offset = (size - w) // 2
        
        # 复制图像到中心
        square[y_offset:y_offset + h, x_offset:x_offset + w] = binary_img
        
        return square


if __name__ == "__main__":
    detector = GridDetector()
    print("✅ GridDetector 加载成功")
    print("   - 支持 find_contours(): 查找轮廓")
    print("   - 支持 find_largest_contour(): 找最大轮廓")
    print("   - 支持 order_points(): 角点排序")
    print("   - 支持 get_warped_image(): 透视变换")
    print("   - 支持 split_into_cells(): 分割单元格")
    print("   - 支持 detect_and_split(): 完整流程")
