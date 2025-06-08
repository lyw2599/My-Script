import sys
import os
import win32gui
import win32con
import win32api
import tkinter as tk
from tkinter import ttk, messagebox
from ctypes import windll
import threading
import time
import pywintypes

# 使任务栏图标正常显示
windll.shell32.SetCurrentProcessExplicitAppUserModelID("WindowTopmostTool.3.0")

class WindowTopmostTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("窗口置顶工具")
        self.root.geometry("400x220")
        self.root.resizable(False, False)
        
        # 设置图标（如果有）
        try:
            self.root.iconbitmap(self.resource_path("icon.ico"))
        except:
            pass
        
        self.target_hwnd = None
        self.target_title = ""
        self.window_list = []
        self.refresh_thread = None
        self.stop_refresh = False
        
        self.create_ui()
        self.start_window_refresh()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def resource_path(self, relative_path):
        """获取资源的绝对路径，用于打包后访问资源文件"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def create_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 窗口选择部分
        select_frame = ttk.LabelFrame(main_frame, text="选择窗口")
        select_frame.pack(fill="x", pady=5)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            select_frame,
            text="刷新列表",
            command=self.manual_refresh,
            width=10
        )
        refresh_btn.pack(side="right", padx=5)
        
        # 窗口下拉框
        self.window_var = tk.StringVar()
        self.window_cb = ttk.Combobox(
            select_frame,
            textvariable=self.window_var,
            state="readonly",
            width=40
        )
        self.window_cb.pack(side="left", fill="x", expand=True, padx=5)
        self.window_cb.bind("<<ComboboxSelected>>", self.on_window_select)
        
        # 操作按钮部分
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)
        
        # 置顶/取消置顶按钮
        self.topmost_btn = ttk.Button(
            btn_frame,
            text="置顶窗口",
            state="disabled",
            command=self.toggle_topmost,
            width=15
        )
        self.topmost_btn.pack(side="left", padx=5)
        
        # 取消置顶所有窗口按钮
        self.cancel_all_btn = ttk.Button(
            btn_frame,
            text="取消所有置顶",
            command=self.safe_cancel_all_topmost,
            width=15
        )
        self.cancel_all_btn.pack(side="right", padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief="sunken",
            anchor="center",
            wraplength=380
        )
        status_bar.pack(fill="x", pady=5)
        self.update_status("就绪")
    
    def start_window_refresh(self):
        """启动窗口列表刷新线程"""
        self.stop_refresh = False
        self.refresh_thread = threading.Thread(
            target=self.auto_refresh_windows,
            daemon=True
        )
        self.refresh_thread.start()
    
    def auto_refresh_windows(self):
        """自动刷新窗口列表"""
        while not self.stop_refresh:
            self.refresh_window_list()
            time.sleep(2)  # 每2秒刷新一次
    
    def manual_refresh(self):
        """手动刷新窗口列表"""
        self.update_status("正在刷新窗口列表...")
        self.refresh_window_list()
        self.update_status("窗口列表已刷新")
    
    def refresh_window_list(self):
        """刷新窗口列表"""
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    self.window_list.append((title, hwnd))
        
        self.window_list = []
        win32gui.EnumWindows(enum_windows_callback, None)
        
        # 去重并排序
        unique_windows = {}
        for title, hwnd in self.window_list:
            if title not in unique_windows:
                unique_windows[title] = hwnd
        
        sorted_windows = sorted(unique_windows.items(), key=lambda x: x[0])
        
        # 更新下拉框
        window_titles = [title for title, _ in sorted_windows]
        current_selection = self.window_var.get()
        
        self.root.after(0, lambda: self.update_window_combobox(window_titles, current_selection))
    
    def update_window_combobox(self, window_titles, current_selection):
        """更新下拉框内容"""
        self.window_cb["values"] = window_titles
        if current_selection in window_titles:
            self.window_var.set(current_selection)
        elif window_titles:
            self.window_var.set(window_titles[0])
            self.on_window_select()
    
    def on_window_select(self, event=None):
        """当下拉框选择变化时"""
        selected_title = self.window_var.get()
        if not selected_title:
            return
        
        # 查找对应的窗口句柄
        for title, hwnd in self.window_list:
            if title == selected_title:
                self.target_hwnd = hwnd
                self.target_title = title
                self.update_status(f"已选择窗口: {title}")
                
                # 检查窗口是否置顶
                try:
                    style = win32gui.GetWindowLong(self.target_hwnd, win32con.GWL_EXSTYLE)
                    is_topmost = style & win32con.WS_EX_TOPMOST
                    
                    self.topmost_btn.config(
                        text="取消置顶" if is_topmost else "置顶窗口",
                        state="normal"
                    )
                except pywintypes.error as e:
                    self.update_status(f"无法访问窗口: {e.strerror}")
                    self.topmost_btn.config(state="disabled")
                break
    
    def toggle_topmost(self):
        """切换窗口置顶状态"""
        if not self.target_hwnd:
            return
        
        # 检查窗口是否仍然存在
        if not win32gui.IsWindow(self.target_hwnd):
            self.update_status("目标窗口已关闭")
            self.topmost_btn.config(state="disabled")
            return
        
        try:
            # 获取当前置顶状态
            style = win32gui.GetWindowLong(self.target_hwnd, win32con.GWL_EXSTYLE)
            is_topmost = style & win32con.WS_EX_TOPMOST
            
            if is_topmost:
                # 取消置顶
                self.safe_set_window_pos(
                    self.target_hwnd,
                    win32con.HWND_NOTOPMOST,
                    "取消置顶",
                    f"已取消置顶: {self.target_title}"
                )
            else:
                # 设置置顶
                self.safe_set_window_pos(
                    self.target_hwnd,
                    win32con.HWND_TOPMOST,
                    "取消置顶",
                    f"已置顶窗口: {self.target_title}"
                )
        except pywintypes.error as e:
            self.update_status(f"操作失败: {e.strerror}")
    
    def safe_set_window_pos(self, hwnd, pos_flag, btn_text, success_msg):
        """安全地设置窗口位置，处理权限问题"""
        try:
            # 尝试获取进程ID
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            # 尝试打开进程检查权限
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, process_id)
            if process:
                win32api.CloseHandle(process)
            
            # 如果有权限，尝试设置窗口位置
            win32gui.SetWindowPos(
                hwnd,
                pos_flag,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
            self.topmost_btn.config(text=btn_text)
            self.update_status(success_msg)
        except pywintypes.error as e:
            if e.winerror == 5:  # 拒绝访问
                self.update_status(f"无权限修改窗口: {self.target_title}")
            else:
                self.update_status(f"操作失败: {e.strerror}")
        except Exception as e:
            self.update_status(f"发生错误: {str(e)}")
    
    def safe_cancel_all_topmost(self):
        """安全地取消所有窗口的置顶状态"""
        count = 0
        failed = 0
        protected = 0
        
        for _, hwnd in self.window_list:
            if not win32gui.IsWindow(hwnd):
                continue
            
            try:
                # 检查窗口是否置顶
                style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                if style & win32con.WS_EX_TOPMOST:
                    # 尝试取消置顶
                    try:
                        win32gui.SetWindowPos(
                            hwnd,
                            win32con.HWND_NOTOPMOST,
                            0, 0, 0, 0,
                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                        )
                        count += 1
                    except pywintypes.error as e:
                        if e.winerror == 5:  # 拒绝访问
                            protected += 1
                        else:
                            failed += 1
            except:
                failed += 1
        
        status_msg = f"已取消 {count} 个窗口的置顶状态"
        if failed > 0:
            status_msg += f"，{failed} 个操作失败"
        if protected > 0:
            status_msg += f"，{protected} 个受保护窗口无法修改"
        
        self.update_status(status_msg)
        if self.target_hwnd:
            self.topmost_btn.config(text="置顶窗口")
    
    def update_status(self, message):
        """更新状态显示"""
        self.status_var.set(message)
        self.root.update()
    
    def on_close(self):
        """关闭窗口时的清理工作"""
        self.stop_refresh = True
        if self.refresh_thread and self.refresh_thread.is_alive():
            self.refresh_thread.join(timeout=1)
        self.root.destroy()

if __name__ == "__main__":
    import win32process
    WindowTopmostTool()