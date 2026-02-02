"""
Sudoku Extractor GUI - 简洁版
点击选择图片，一键转换为 Excel
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from image_processor import ImagePreprocessor
from grid_detector import GridDetector
from ocr_engine import OCREngine
from excel_writer import ExcelWriter


class SudokuGUI:
    """数独提取器 GUI"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📷 数独提取器")
        self.root.geometry("420x320")
        self.root.resizable(False, False)

        # 变量
        self.image_path = tk.StringVar()
        self.output_path = tk.StringVar(value=str(Path.home() / "Desktop" / "sudoku_output.xlsx"))
        self.preprocessor = None
        self.detector = None
        self.ocr = None
        self.writer = None

        # 构建界面
        self._build_ui()
        self._init_ocr()

    def _init_ocr(self):
        """初始化OCR引擎（后台加载）"""
        self.status_label.configure(text="正在加载OCR引擎...")
        self.root.update()

        try:
            self.preprocessor = ImagePreprocessor(threshold=128)
            self.detector = GridDetector(debug=False)
            self.ocr = OCREngine()
            self.writer = ExcelWriter()
            self.status_label.configure(text="就绪，可以开始转换")
        except Exception as e:
            self.status_label.configure(text="OCR加载失败")
            messagebox.showerror("错误", f"OCR初始化失败:\n{e}")

    def _build_ui(self):
        """构建界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(
            main_frame,
            text="📷 数独图片转 Excel",
            font=("Microsoft YaHei", 18, "bold")
        ).pack(pady=(0, 5))

        ttk.Label(
            main_frame,
            text="将数独图片识别并导出为表格",
            font=("Microsoft YaHei", 9),
            foreground="gray"
        ).pack(pady=(0, 20))

        # 图片选择区域
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(select_frame, text="图片:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)

        self.path_entry = ttk.Entry(select_frame, textvariable=self.image_path, width=28)
        self.path_entry.pack(side=tk.LEFT, padx=(8, 5))

        ttk.Button(
            select_frame,
            text="选择图片...",
            command=self._select_file,
            width=10
        ).pack(side=tk.LEFT)

        # 输出路径
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(output_frame, text="输出:", font=("Microsoft YaHei", 10)).pack(side=tk.LEFT)

        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=28)
        self.output_entry.pack(side=tk.LEFT, padx=(8, 5))

        ttk.Button(
            output_frame,
            text="浏览...",
            command=self._select_output,
            width=10
        ).pack(side=tk.LEFT)

        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="识别预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        self.preview_text = tk.Text(
            preview_frame,
            height=8,
            width=40,
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg="#f5f5f5"
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # 转换按钮
        self.convert_btn = ttk.Button(
            main_frame,
            text="开始转换 →",
            command=self._convert,
            state=tk.DISABLED
        )
        self.convert_btn.pack(fill=tk.X)

        # 状态栏
        self.status_label = ttk.Label(
            main_frame,
            text="初始化中...",
            font=("Microsoft YaHei", 9),
            foreground="gray"
        )
        self.status_label.pack(pady=(10, 0))

    def _select_file(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择数独图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.image_path.set(file_path)
            self.convert_btn.configure(state=tk.NORMAL)
            self.status_label.configure(text="已选择图片，点击转换")

    def _select_output(self):
        """选择输出位置"""
        current = self.image_path.get()
        initial_file = Path(current).stem + "_sudoku.xlsx" if current else "sudoku_output.xlsx"

        file_path = filedialog.asksaveasfilename(
            title="保存Excel文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")],
            initialfile=initial_file
        )
        if file_path:
            self.output_path.set(file_path)

    def _convert(self):
        """执行转换"""
        image_path = self.image_path.get()
        output_path = self.output_path.get()

        if not image_path or not os.path.exists(image_path):
            messagebox.showerror("错误", "请先选择图片文件")
            return

        if not output_path:
            messagebox.showerror("错误", "请设置输出路径")
            return

        # 禁用按钮
        self.convert_btn.configure(state=tk.DISABLED)

        try:
            # 1. 预处理
            self.status_label.configure(text="正在预处理图像...")
            self.root.update()
            binary, arr = self.preprocessor.preprocess(image_path)

            # 2. 检测网格
            self.status_label.configure(text="正在检测数独网格...")
            self.root.update()
            cells = self.detector.detect_and_split(arr)

            # 3. OCR识别
            self.status_label.configure(text="正在识别数字...")
            self.root.update()
            grid = self.ocr.extract_grid_with_empty_check(cells)

            # 4. 显示预览
            self._show_preview(grid)

            # 5. 保存Excel
            self.status_label.configure(text="正在保存Excel...")
            self.root.update()
            self.writer.write_with_metadata(grid, os.path.basename(image_path), output_path)

            self.status_label.configure(text="完成！✅")
            messagebox.showinfo("成功", f"✅ 已保存到:\n{output_path}")

        except Exception as e:
            self.status_label.configure(text="处理失败 ❌")
            messagebox.showerror("错误", f"处理失败:\n{str(e)}")

        finally:
            self.convert_btn.configure(state=tk.NORMAL)

    def _show_preview(self, grid):
        """显示识别预览"""
        self.preview_text.configure(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)

        lines = []
        lines.append("┌───────┬───────┬───────┐")
        for row in range(9):
            row_data = []
            for col in range(9):
                val = grid[row * 9 + col]
                row_data.append(str(val) if val else ".")
            
            # 每3列加分隔线
            line = "│ " + "  ".join(row_data[:3]) + " │ " + \
                          "  ".join(row_data[3:6]) + " │ " + \
                          "  ".join(row_data[6:]) + " │"
            lines.append(line)
            
            if row % 3 == 2 and row < 8:
                lines.append("├───────┼───────┼───────┤")
        
        lines.append("└───────┴───────┴───────┘")
        
        self.preview_text.insert(tk.END, "\n".join(lines))
        self.preview_text.configure(state=tk.DISABLED)

    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    app = SudokuGUI()
    app.run()


if __name__ == "__main__":
    main()
