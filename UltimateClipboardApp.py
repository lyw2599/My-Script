import tkinter as tk
from tkinter import ttk


class UltimateClipboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("终极剪贴板工具")
        
        # 设置窗口默认大小和居中显示（宽度x高度）
        self._set_window_geometry(300, 300)  # 可修改这里的数值
        
        # 存储内容和状态
        self.row_contents = []
        self.current_rows = 5
        self.is_topmost = False
        
        # 创建界面
        self._create_ui()
        self._create_rows()
    
    def _set_window_geometry(self, width, height):
        """设置窗口大小并居中"""
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(100, 100)  # 设置最小窗口大小（可选）
    
    def _create_ui(self):
        """创建界面布局"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮行（顶部单行）
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 添加行按钮
        ttk.Button(
            control_frame,
            text="＋添加行",
            width=8,
            command=self._add_row
        ).pack(side=tk.LEFT, padx=2)
        
        # 删除行按钮
        ttk.Button(
            control_frame,
            text="－删除行",
            width=8,
            command=self._remove_row
        ).pack(side=tk.LEFT, padx=2)
        
        # 窗口置顶按钮
        self.topmost_btn = ttk.Button(
            control_frame,
            text="📌 窗口置顶",
            width=10,
            command=self._toggle_topmost
        )
        self.topmost_btn.pack(side=tk.LEFT, padx=2)
        
        # 行数显示
        self.row_count_label = ttk.Label(
            control_frame,
            text=f"行数: {self.current_rows}",
            width=8
        )
        self.row_count_label.pack(side=tk.RIGHT)
        
        # 内容区域（带滚动条）
        self.canvas = tk.Canvas(main_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.rows_frame = ttk.Frame(self.canvas)
        
        # 配置滚动区域
        self.rows_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.rows_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_rows(self):
        """创建内容行（含粘贴按钮）"""
        # 清除现有行
        for widget in self.rows_frame.winfo_children():
            widget.destroy()
        
        self.entries = []
        self.copy_buttons = []
        self.paste_buttons = []
        
        # 确保内容长度足够
        while len(self.row_contents) < self.current_rows:
            self.row_contents.append("")
        
        # 创建每行内容
        for i in range(self.current_rows):
            row_frame = ttk.Frame(self.rows_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            # 输入框（占60%宽度）
            entry = ttk.Entry(row_frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
            entry.insert(0, self.row_contents[i])
            self.entries.append(entry)
            
            # 复制按钮（固定宽度）
            copy_btn = ttk.Button(
                row_frame,
                text="复制",
                width=5,
                command=lambda idx=i: self._copy_text(idx)
            )
            copy_btn.pack(side=tk.LEFT, padx=2)
            self.copy_buttons.append(copy_btn)
            
            # 粘贴按钮（固定宽度）
            paste_btn = ttk.Button(
                row_frame,
                text="粘贴",
                width=5,
                command=lambda idx=i: self._paste_text(idx)
            )
            paste_btn.pack(side=tk.LEFT)
            self.paste_buttons.append(paste_btn)
        
        # 更新行数显示
        self.row_count_label.config(text=f"行数: {self.current_rows}")
        self._update_scrollregion()
    
    def _save_contents(self):
        """保存当前所有内容"""
        self.row_contents = [entry.get() for entry in self.entries]
    
    def _add_row(self):
        """添加一行"""
        self._save_contents()
        self.current_rows += 1
        self.row_contents.append("")
        self._create_rows()
        self._scroll_to_bottom()
    
    def _remove_row(self):
        """删除最后一行"""
        if self.current_rows > 1:
            self._save_contents()
            self.current_rows -= 1
            self.row_contents.pop()
            self._create_rows()
    
    def _toggle_topmost(self):
        """切换窗口置顶"""
        self.is_topmost = not self.is_topmost
        self.root.attributes('-topmost', self.is_topmost)
        self.topmost_btn.config(
            text="✅ 取消置顶" if self.is_topmost else "📌 窗口置顶"
        )
    
    def _copy_text(self, index):
        """复制文本到剪贴板"""
        text = self.entries[index].get()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.copy_buttons[index].config(text="✓已复制")
            self.root.after(1000, lambda: self.copy_buttons[index].config(text="复制"))
    
    def _paste_text(self, index):
        """从剪贴板粘贴文本"""
        try:
            text = self.root.clipboard_get()
            if text:
                self.entries[index].delete(0, tk.END)
                self.entries[index].insert(0, text)
                self.paste_buttons[index].config(text="✓已粘贴")
                self.root.after(1000, lambda: self.paste_buttons[index].config(text="粘贴"))
        except tk.TclError:
            self.paste_buttons[index].config(text="无内容")
            self.root.after(1000, lambda: self.paste_buttons[index].config(text="粘贴"))
    
    def _update_scrollregion(self):
        """更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        self.canvas.yview_moveto(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateClipboardApp(root)
    root.mainloop()