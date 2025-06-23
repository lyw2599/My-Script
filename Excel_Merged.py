import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pandas as pd
from typing import Union, List

class FileMergerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel 文件合并工具")
        self.root.geometry("800x600")
        
        # Variables
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.merge_mode = tk.StringVar(value="row")
        self.sheet_name = tk.StringVar()
        self.cols_range = tk.StringVar()
        self.rows_range = tk.StringVar()
        self.source_position = tk.StringVar(value="末")  # 修改为中文"首"/"末"
        self.output_format = tk.StringVar(value="excel")
        self.selected_files = []
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Source selection
        source_frame = ttk.LabelFrame(main_frame, text="源文件选择", padding="10")
        source_frame.grid(row=0, column=0, sticky="ew", pady=5)
        
        ttk.Label(source_frame, text="文件/文件夹:").grid(row=0, column=0, sticky="w")
        ttk.Entry(source_frame, textvariable=self.source_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(source_frame, text="浏览文件夹", command=self.browse_folder).grid(row=0, column=2, padx=5)
        ttk.Button(source_frame, text="选择文件", command=self.select_files).grid(row=0, column=3, padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="合并选项", padding="10")
        options_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Merge mode
        ttk.Label(options_frame, text="合并方式:").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(options_frame, text="按行合并", variable=self.merge_mode, value="row", 
                       command=self.update_source_position_label).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(options_frame, text="按列合并", variable=self.merge_mode, value="column",
                       command=self.update_source_position_label).grid(row=0, column=2, sticky="w")
        
        # Sheet selection
        ttk.Label(options_frame, text="Sheet选择 (留空为所有, 多个用逗号分隔):").grid(row=1, column=0, sticky="w")
        ttk.Entry(options_frame, textvariable=self.sheet_name, width=30).grid(row=1, column=1, columnspan=3, sticky="w", padx=5)
        
        # Rows/Cols selection
        ttk.Label(options_frame, text="行范围 (如 5:, :10, 5:10, 1,3,5):").grid(row=2, column=0, sticky="w")
        ttk.Entry(options_frame, textvariable=self.rows_range, width=30).grid(row=2, column=1, columnspan=3, sticky="w", padx=5)
        
        ttk.Label(options_frame, text="列范围 (如 A:, :D, B:D, A,C,E, AA:AC):").grid(row=3, column=0, sticky="w")
        ttk.Entry(options_frame, textvariable=self.cols_range, width=30).grid(row=3, column=1, columnspan=3, sticky="w", padx=5)
        
        # Source position
        self.source_position_label = ttk.Label(options_frame, text="来源信息位置:")
        self.source_position_label.grid(row=4, column=0, sticky="w")
        
        self.source_position_frame = ttk.Frame(options_frame)
        self.source_position_frame.grid(row=4, column=1, columnspan=3, sticky="w")
        
        # 初始设置为行合并模式下的选项
        self.update_source_position_label()
        
        # Output format
        ttk.Label(options_frame, text="输出格式:").grid(row=5, column=0, sticky="w")
        ttk.Radiobutton(options_frame, text="Excel", variable=self.output_format, value="excel").grid(row=5, column=1, sticky="w")
        ttk.Radiobutton(options_frame, text="CSV", variable=self.output_format, value="csv").grid(row=5, column=2, sticky="w")
        
        # Output selection
        output_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="10")
        output_frame.grid(row=2, column=0, sticky="ew", pady=5)
        
        ttk.Label(output_frame, text="输出文件:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(output_frame, text="浏览", command=self.browse_output).grid(row=0, column=2, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=10)
        
        ttk.Button(button_frame, text="开始合并", command=self.start_merge).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).grid(row=4, column=0, sticky="ew", pady=5)
    
    def update_source_position_label(self):
        # 清除原有选项
        for widget in self.source_position_frame.winfo_children():
            widget.destroy()
        
        # 根据合并模式更新选项
        if self.merge_mode.get() == "row":
            self.source_position_label.config(text="来源信息位置:")
            ttk.Radiobutton(self.source_position_frame, text="首列", variable=self.source_position, value="首").pack(side=tk.LEFT)
            ttk.Radiobutton(self.source_position_frame, text="末列", variable=self.source_position, value="末").pack(side=tk.LEFT)
        else:
            self.source_position_label.config(text="来源信息位置:")
            ttk.Radiobutton(self.source_position_frame, text="首行", variable=self.source_position, value="首").pack(side=tk.LEFT)
            ttk.Radiobutton(self.source_position_frame, text="末行", variable=self.source_position, value="末").pack(side=tk.LEFT)
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_path.set(folder)
            self.selected_files = []
    
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="选择Excel/CSV文件",
            filetypes=[("Excel/CSV文件", "*.xlsx *.xls *.csv"), ("所有文件", "*.*")]
        )
        if files:
            self.selected_files = list(files)
            folder = os.path.dirname(files[0])
            self.source_path.set(f"{folder} (已选择 {len(files)} 个文件)")
    
    def browse_output(self):
        if self.output_format.get() == "excel":
            file_ext = ".xlsx"
            file_types = [("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
        else:
            file_ext = ".csv"
            file_types = [("CSV文件", "*.csv"), ("所有文件", "*.*")]
        
        initial_file = f"merged_data{file_ext}"
        output_file = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            initialfile=initial_file,
            filetypes=file_types
        )
        if output_file:
            self.output_path.set(output_file)
    
    def parse_flex_range(self, range_str: str, max_val: int, is_col: bool = False) -> Union[slice, List[int]]:
        if not range_str or range_str.strip() == "":
            return slice(None)
        
        # Handle comma-separated discrete values
        if "," in range_str:
            parts = [p.strip() for p in range_str.split(",") if p.strip()]
            indices = []
            for part in parts:
                if is_col:
                    # Handle Excel column letters (single or multiple letters)
                    if part.isalpha():
                        col = 0
                        for i, c in enumerate(reversed(part.upper())):
                            col += (ord(c) - ord('A') + 1) * (26 ** i)
                        idx = col - 1  # Convert to 0-based index
                        if 0 <= idx < max_val:
                            indices.append(idx)
                    elif part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < max_val:
                            indices.append(idx)
                else:
                    if part.isdigit():
                        idx = int(part) - 1
                        if 0 <= idx < max_val:
                            indices.append(idx)
            return sorted(list(set(indices))) if indices else slice(None)
        
        # Handle range format
        parts = range_str.split(':')
        if len(parts) != 2:
            return slice(None)
        
        start, end = parts
        
        if is_col:
            # Convert Excel column letters to indices
            def col_to_index(col_str):
                if not col_str:
                    return None
                if col_str.isdigit():
                    return int(col_str) - 1
                col = 0
                for i, c in enumerate(reversed(col_str.upper())):
                    if not c.isalpha():
                        return None
                    col += (ord(c) - ord('A') + 1) * (26 ** i)
                return col - 1
            
            start_idx = col_to_index(start) if start else 0
            end_idx = col_to_index(end) if end else max_val
            
            if start_idx is None or end_idx is None:
                return slice(None)
            
            if end_idx is not None:
                end_idx += 1  # Make end_idx exclusive
            
            return slice(start_idx, end_idx)
        
        # Handle row ranges
        start_idx = int(start) - 1 if start else 0
        end_idx = int(end) if end else max_val
        return slice(start_idx, end_idx)
    
    def read_file(self, file_path, file_type, sheet_name=None):
        if file_type == 'csv':
            encodings = ['utf-8', 'gbk', 'latin1', 'utf-16']
            for enc in encodings:
                try:
                    return pd.read_csv(file_path, header=None, encoding=enc)
                except (UnicodeDecodeError, UnicodeError):
                    continue
            return pd.read_csv(file_path, header=None, errors='replace')
        elif file_type in ('xlsx', 'xls'):
            if sheet_name:
                return pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            else:
                with pd.ExcelFile(file_path) as xls:
                    return pd.read_excel(xls, sheet_name=xls.sheet_names[0], header=None)
        return None
    
    def start_merge(self):
        source_path = self.source_path.get()
        output_file = self.output_path.get()
        
        if not source_path:
            messagebox.showerror("错误", "请选择源文件或文件夹")
            return
        
        if not output_file:
            messagebox.showerror("错误", "请选择输出文件路径")
            return
        
        try:
            self.status_var.set("正在合并文件...")
            self.root.update_idletasks()
            
            all_data = []
            max_cols = 0
            
            # Get files to process
            if self.selected_files:
                files_to_process = self.selected_files
            else:
                files_to_process = [
                    os.path.join(source_path, f) for f in os.listdir(source_path) 
                    if f.lower().endswith(('.csv', '.xlsx', '.xls'))
                ]
            
            # Get sheet names to process
            sheet_names = []
            if self.sheet_name.get():
                sheet_names = [s.strip() for s in self.sheet_name.get().split(",") if s.strip()]
            
            for file_path in files_to_process:
                try:
                    _, ext = os.path.splitext(file_path)
                    file_type = ext[1:].lower() if ext else ''
                    
                    if file_type not in ('csv', 'xlsx', 'xls'):
                        continue
                        
                    # Process sheets
                    if file_type in ('xlsx', 'xls'):
                        if sheet_names:
                            sheets = sheet_names
                        else:
                            with pd.ExcelFile(file_path) as xls:
                                sheets = xls.sheet_names
                    else:
                        sheets = [None]
                        
                    for sheet in sheets:
                        df = self.read_file(file_path, file_type, sheet)
                        if df is None or df.empty:
                            continue
                        
                        # Apply row and column selection
                        rows = self.rows_range.get()
                        cols = self.cols_range.get()
                        
                        if rows:
                            row_indices = self.parse_flex_range(rows, len(df))
                            if isinstance(row_indices, list):
                                df = df.iloc[row_indices, :]
                            else:
                                df = df.iloc[row_indices, :]
                        
                        if cols:
                            col_indices = self.parse_flex_range(cols, len(df.columns), is_col=True)
                            if isinstance(col_indices, list):
                                df = df.iloc[:, col_indices]
                            else:
                                df = df.iloc[:, col_indices]
                        
                        # Record max columns
                        current_cols = len(df.columns)
                        if current_cols > max_cols:
                            max_cols = current_cols
                        
                        # Add source info
                        file_name = os.path.basename(file_path)
                        source_info = pd.DataFrame({
                            'source_file': [file_name] * len(df),
                            'sheet_name': [sheet if sheet else ""] * len(df)
                        })
                        
                        if self.merge_mode.get() == "row":
                            # 行合并模式：来源信息作为列添加
                            if self.source_position.get() == "首":
                                df = pd.concat([source_info, df], axis=1)
                            else:
                                df = pd.concat([df, source_info], axis=1)
                        else:
                            # 列合并模式：来源信息作为行添加
                            source_row = pd.DataFrame([[file_name, sheet if sheet else ""] + [""]*(len(df.columns)-2)], 
                                                     columns=df.columns)
                            if self.source_position.get() == "首":
                                df = pd.concat([source_row, df], axis=0)
                            else:
                                df = pd.concat([df, source_row], axis=0)
                        
                        all_data.append(df)
                        
                except Exception as e:
                    self.status_var.set(f"处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
                    self.root.update_idletasks()
                    continue
            
            if not all_data:
                messagebox.showinfo("信息", "没有找到有效数据")
                self.status_var.set("没有找到有效数据")
                return
            
            # Standardize columns
            for i, df in enumerate(all_data):
                if len(df.columns) < max_cols:
                    padding_cols = max_cols - len(df.columns)
                    padding_df = pd.DataFrame(
                        [[None]*padding_cols for _ in range(len(df))],
                        columns=[f'col_{j}' for j in range(len(df.columns), len(df.columns)+padding_cols)]
                    )
                    all_data[i] = pd.concat([df, padding_df], axis=1)
            
            # Merge data
            if self.merge_mode.get() == "column":
                max_rows = max(len(df) for df in all_data)
                for i, df in enumerate(all_data):
                    if len(df) < max_rows:
                        padding = pd.DataFrame(
                            [[None]*len(df.columns)]*(max_rows - len(df)),
                            columns=df.columns
                        )
                        all_data[i] = pd.concat([df, padding], axis=0)
                merged_df = pd.concat(all_data, axis=1)
            else:
                merged_df = pd.concat(all_data, axis=0, ignore_index=True)
            
            # Save result
            if output_file.lower().endswith('.csv'):
                merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            else:
                merged_df.to_excel(output_file, index=False)
            
            self.status_var.set(f"合并完成 → {output_file}")
            messagebox.showinfo("成功", f"文件合并完成\n保存到: {output_file}")
            
        except Exception as e:
            messagebox.showerror("错误", f"合并过程中出错: {str(e)}")
            self.status_var.set(f"错误: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMergerGUI(root)
    root.mainloop()
