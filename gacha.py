import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
from collections import defaultdict
import json
import csv
import os
from datetime import datetime

class RandomNumberGenerator:
    def __init__(self, master):
        self.master = master
        master.title("随机数抽奖系统")
        
        # 设置应用图标和主题
        self.set_style()
        
        # 初始化变量
        self.is_rolling = False
        self.excluded_numbers = []
        self.current_number = None
        self.history = []  # 存储抽奖历史记录
        
        # 创建界面组件
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
        
    def set_style(self):
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("Header.TLabel", font=("微软雅黑", 12, "bold"))
        self.style.configure("Number.TLabel", font=("Impact", 52), anchor="center")
        
    def bind_events(self):
        # 绑定键盘快捷键
        self.master.bind("<space>", lambda event: self.toggle_roll())
        self.master.bind("<Return>", lambda event: self.record_number())
        self.master.bind("<BackSpace>", lambda event: self.undo_record())
        self.master.bind("<Control-s>", lambda event: self.save_config())
        self.master.bind("<Control-o>", lambda event: self.load_config())
        self.master.bind("<Control-e>", lambda event: self.export_results())
        
        # 绑定窗口调整事件
        self.master.bind("<Configure>", self.on_resize)
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 顶部提示
        header = ttk.Label(main_frame, text="随机数抽奖系统", style="Header.TLabel")
        header.pack(pady=(0, 10))
        
        # 左侧参数和控制区域
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 参数设置区域 (使用LabelFrame美化)
        param_frame = ttk.LabelFrame(left_frame, text="参数设置", padding=10)
        param_frame.pack(fill=tk.X, pady=5)
        
        # 使用grid布局参数
        ttk.Label(param_frame, text="最小值:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.min_entry = ttk.Entry(param_frame, width=8)
        self.min_entry.grid(row=0, column=1, padx=5, pady=5)
        self.min_entry.insert(0, "100")
        
        ttk.Label(param_frame, text="最大值:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.max_entry = ttk.Entry(param_frame, width=8)
        self.max_entry.grid(row=0, column=3, padx=5, pady=5)
        self.max_entry.insert(0, "500")
        
        ttk.Label(param_frame, text="步长:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.step_entry = ttk.Entry(param_frame, width=8)
        self.step_entry.grid(row=1, column=1, padx=5, pady=5)
        self.step_entry.insert(0, "1")
        
        # 显示区域
        display_frame = ttk.LabelFrame(left_frame, text="当前抽取", padding=10)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.number_label = ttk.Label(
            display_frame, 
            text="点击开始按钮", 
            style="Number.TLabel",
            anchor=tk.CENTER,
        )
        self.number_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 控制按钮区域
        button_frame = ttk.Frame(left_frame, padding=5)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 使用图标美化按钮
        self.start_btn = ttk.Button(
            button_frame, 
            text="开始 (Space)", 
            command=self.toggle_roll,
            width=15
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.record_btn = ttk.Button(
            button_frame, 
            text="记录 (Enter)", 
            command=self.record_number,
            width=15
        )
        self.record_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 第二行按钮
        button_frame2 = ttk.Frame(left_frame, padding=5)
        button_frame2.pack(fill=tk.X, pady=5)
        
        self.undo_btn = ttk.Button(
            button_frame2, 
            text="撤销 (Backspace)", 
            command=self.undo_record,
            width=15
        )
        self.undo_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.reset_btn = ttk.Button(
            button_frame2, 
            text="重置全部", 
            command=self.confirm_reset_all,
            width=15
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 右侧记录列表和功能区域
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # 记录列表区域
        list_frame = ttk.LabelFrame(right_frame, text="已抽取记录", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 列表和滚动条
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.listbox = tk.Listbox(
            list_container, 
            height=10,
            selectmode=tk.EXTENDED,  # 允许多选
            font=("微软雅黑", 10),
            activestyle="dotbox",
            exportselection=False
        )
        scrollbar = ttk.Scrollbar(
            list_container, 
            orient=tk.VERTICAL, 
            command=self.listbox.yview
        )
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 记录操作区域
        list_actions = ttk.Frame(list_frame)
        list_actions.pack(fill=tk.X, pady=(5, 0))
        
        self.delete_btn = ttk.Button(
            list_actions,
            text="删除选中",
            command=self.delete_selected,
            width=10
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.export_btn = ttk.Button(
            list_actions,
            text="导出记录",
            command=self.export_results,
            width=10
        )
        self.export_btn.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
        
        # 手动添加区域
        manual_frame = ttk.LabelFrame(right_frame, text="手动添加", padding=10)
        manual_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.manual_entry = ttk.Entry(manual_frame)
        self.manual_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.add_btn = ttk.Button(
            manual_frame,
            text="添加",
            command=self.manual_add,
            width=8
        )
        self.add_btn.pack(side=tk.RIGHT, padx=5)
        
        # 配置保存/加载区域
        config_frame = ttk.Frame(right_frame, padding=5)
        config_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.save_btn = ttk.Button(
            config_frame,
            text="保存配置 (Ctrl+S)",
            command=self.save_config,
            width=15
        )
        self.save_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.load_btn = ttk.Button(
            config_frame,
            text="加载配置 (Ctrl+O)",
            command=self.load_config,
            width=15
        )
        self.load_btn.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(
            self.master, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_resize(self, event=None):
        # 响应窗口大小变化
        if hasattr(self, 'number_label'):
            # 调整字体大小以适应窗口
            width = self.master.winfo_width()
            if width < 800:
                font_size = 48
            else:
                font_size = 56
                
            self.style.configure("Number.TLabel", font=("Impact", font_size))
    
    def validate_input(self):
        """验证输入参数"""
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            step = int(self.step_entry.get())
            
            if min_val > max_val:
                messagebox.showerror("输入错误", "最小值不能大于最大值")
                return None
                
            if step <= 0:
                messagebox.showerror("输入错误", "步长必须为正整数")
                return None
                
            return min_val, max_val, step
            
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的整数")
            return None

    def get_valid_candidates(self):
        """获取有效的候选数字"""
        result = self.validate_input()
        if not result:
            return None
            
        min_val, max_val, step = result
        candidates = list(range(min_val, max_val + 1, step))
        return [num for num in candidates if num not in self.excluded_numbers]
    
    def toggle_roll(self):
        """切换开始/停止状态"""
        if self.is_rolling:
            self.stop_rolling()
        else:
            self.start_rolling()
    
    def start_rolling(self):
        """开始滚动随机数"""
        candidates = self.get_valid_candidates()
        
        if not candidates:
            messagebox.showwarning("警告", "没有可用的候选数字！")
            return
            
        self.is_rolling = True
        self.start_btn.config(text="停止 (Space)")
        self.status_var.set("正在抽取...")
        self.roll_number(candidates)
    
    def stop_rolling(self):
        """停止滚动随机数"""
        self.is_rolling = False
        self.start_btn.config(text="开始 (Space)")
        self.status_var.set("就绪")
    
    def roll_number(self, candidates):
        """滚动随机数的核心逻辑"""
        if self.is_rolling and candidates:
            self.current_number = random.choice(candidates)
            self.number_label.config(text=str(self.current_number))
            self.master.after(15, lambda: self.roll_number(candidates))
    
    def record_number(self):
        """记录当前数字"""
        if self.current_number is not None and not self.is_rolling:
            if self.current_number not in self.excluded_numbers:
                self.excluded_numbers.append(self.current_number)
                self.update_list_display()
                
                # 记录抽取历史
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.history.append({
                    "number": self.current_number,
                    "timestamp": timestamp
                })
                
                self.number_label.config(text="已记录")
                self.status_var.set(f"已记录数字: {self.current_number}")
                self.current_number = None
            else:
                messagebox.showinfo("提示", "该数字已在记录列表中")
        elif self.is_rolling:
            self.stop_rolling()
    
    def confirm_reset_all(self):
        """确认重置全部"""
        result = messagebox.askokcancel("确认", "确定要重置所有设置和记录吗？")
        if result:
            self.reset_all()
    
    def reset_all(self):
        """重置所有设置和记录"""
        self.stop_rolling()
        self.excluded_numbers = []
        self.history = []
        self.listbox.delete(0, tk.END)
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, "100")
        self.max_entry.delete(0, tk.END)
        self.max_entry.insert(0, "500")
        self.step_entry.delete(0, tk.END)
        self.step_entry.insert(0, "1")
        self.number_label.config(text="点击开始按钮")
        self.status_var.set("已重置所有设置和记录")

    def update_list_display(self):
        """更新列表框显示带序号的记录"""
        self.listbox.delete(0, tk.END)  # 清空现有列表
        # 重新插入带序号的记录
        for idx, num in enumerate(self.excluded_numbers, start=1):
            self.listbox.insert(tk.END, f"{idx}. {num}")

    def manual_add(self):
        """手动添加数字"""
        num_str = self.manual_entry.get()
        if not num_str:
            return
            
        try:
            num = int(num_str)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数")
            return
            
        if num in self.excluded_numbers:
            messagebox.showwarning("警告", "该数字已在记录中")
            return
            
        self.excluded_numbers.append(num)
        self.update_list_display()
        self.manual_entry.delete(0, tk.END)
        self.status_var.set(f"已添加: {num}")

        # 记录历史
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "number": num,
            "timestamp": timestamp,
            "method": "manual"
        })

    def undo_record(self):
        """撤销最后一个记录"""
        if self.excluded_numbers:
            removed_num = self.excluded_numbers.pop()
            if self.history:
                self.history.pop()
            self.update_list_display()
            self.status_var.set(f"已撤销: {removed_num}")
        else:
            self.status_var.set("没有可撤销的记录")

    def delete_selected(self):
        """删除选中的记录项"""
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showinfo("提示", "请先选择要删除的记录")
            return
            
        # 从大到小排序索引，以便从后向前删除不会影响索引
        indices = sorted(selected_indices, reverse=True)
        
        # 确认删除
        if len(indices) == 1:
            confirm_msg = f"确定要删除数字 {self.excluded_numbers[indices[0]]} 吗？"
        else:
            confirm_msg = f"确定要删除这 {len(indices)} 个选中的记录吗？"
            
        if not messagebox.askyesno("确认删除", confirm_msg):
            return
        
        # 执行删除
        for idx in indices:
            del self.excluded_numbers[idx]
            
        # 从历史中也删除相应记录
        # 注意：这里简化处理，直接重置历史
        self.history = []
        
        self.update_list_display()
        self.status_var.set(f"已删除 {len(indices)} 条记录")

    def save_config(self, event=None):
        """保存配置和记录到文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            title="保存配置"
        )
        
        if not file_path:
            return
            
        config = {
            "min_value": self.min_entry.get(),
            "max_value": self.max_entry.get(),
            "step": self.step_entry.get(),
            "excluded_numbers": self.excluded_numbers,
            "history": self.history,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"配置已保存到: {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存配置: {str(e)}")

    def load_config(self, event=None):
        """从文件加载配置和记录"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            title="加载配置"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # 确认加载
            confirm = messagebox.askyesno(
                "确认加载", 
                f"确定要加载配置 {os.path.basename(file_path)}？\n这将覆盖当前的所有设置和记录。"
            )
            
            if not confirm:
                return
                
            # 应用配置
            self.min_entry.delete(0, tk.END)
            self.min_entry.insert(0, config.get("min_value", "100"))
            
            self.max_entry.delete(0, tk.END)
            self.max_entry.insert(0, config.get("max_value", "500"))
            
            self.step_entry.delete(0, tk.END)
            self.step_entry.insert(0, config.get("step", "1"))
            
            self.excluded_numbers = config.get("excluded_numbers", [])
            self.history = config.get("history", [])
            
            self.update_list_display()
            self.number_label.config(text="已加载配置")
            self.status_var.set(f"已加载配置: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("加载失败", f"无法加载配置: {str(e)}")

    def export_results(self, event=None):
        """导出抽奖结果"""
        if not self.excluded_numbers:
            messagebox.showinfo("提示", "没有记录可以导出")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV文件", "*.csv"),
                ("Excel文件", "*.xlsx"),
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ],
            title="导出记录"
        )
        
        if not file_path:
            return
            
        try:
            # 根据文件扩展名选择导出格式
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                self.export_to_csv(file_path)
            elif ext == '.xlsx':
                self.export_to_excel(file_path)
            elif ext == '.txt':
                self.export_to_txt(file_path)
            else:
                self.export_to_csv(file_path)  # 默认CSV
                
            self.status_var.set(f"记录已导出到: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"无法导出记录: {str(e)}")
    
    def export_to_csv(self, file_path):
        """导出为CSV格式"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["序号", "抽取数字", "时间"])
            
            for idx, num in enumerate(self.excluded_numbers, 1):
                # 尝试从历史记录中找到对应时间
                timestamp = ""
                for record in self.history:
                    if record.get("number") == num:
                        timestamp = record.get("timestamp", "")
                        break
                        
                writer.writerow([idx, num, timestamp])

    def export_to_excel(self, file_path):
        """导出为Excel格式"""
        try:
            import pandas as pd
            
            data = []
            for idx, num in enumerate(self.excluded_numbers, 1):
                # 尝试从历史记录中找到对应时间
                timestamp = ""
                for record in self.history:
                    if record.get("number") == num:
                        timestamp = record.get("timestamp", "")
                        break
                        
                data.append({"序号": idx, "抽取数字": num, "时间": timestamp})
                
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
        except ImportError:
            messagebox.showerror("导出失败", "导出Excel需要安装pandas库")
            self.export_to_csv(file_path)  # 回退到CSV
    
    def export_to_txt(self, file_path):
        """导出为TXT格式"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("抽奖记录\n")
            f.write("="*40 + "\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"记录数量: {len(self.excluded_numbers)}\n")
            f.write("="*40 + "\n\n")
            
            for idx, num in enumerate(self.excluded_numbers, 1):
                # 尝试从历史记录中找到对应时间
                timestamp = ""
                for record in self.history:
                    if record.get("number") == num:
                        timestamp = record.get("timestamp", "")
                        break
                        
                f.write(f"{idx}. 数字: {num}")
                if timestamp:
                    f.write(f" (时间: {timestamp})")
                f.write("\n")


class EnhancedRandomNumberGenerator(RandomNumberGenerator):
    """增强版随机数生成器，继承基本功能并扩展"""
    def __init__(self, master):
        super().__init__(master)
        
        # 在状态栏添加模式显示
        self.status_var.set("增强模式就绪")


class UniformRandomGenerator(RandomNumberGenerator):
    """均匀随机数生成器，使用特殊算法确保更均匀的分布"""
    def __init__(self, master):
        super().__init__(master)
        
        # 固定邻域参数配置
        self._neighborhood_radius = 75      # 邻域影响半径
        self._base_decay = 0.38             # 主衰减系数
        self._neighbor_decay = 0.85         # 邻域衰减系数
        self._min_weight = 0.18             # 最小权重限制
        
        # 历史记录窗口
        self.history_window = []
        
        # 在状态栏添加模式显示
        self.status_var.set("均匀分布模式就绪")

    def calculate_weights(self, candidates):
        """优化的权重计算算法（固定参数版）"""
        weights = {}
        heatmap = defaultdict(float)
        
        # 构建热度分布图
        for num in self.history_window[-10:]:
            # 主热度衰减
            heatmap[num] += 1.0
            
            # 邻域影响衰减
            start = max(min(candidates), num - self._neighborhood_radius)
            end = min(max(candidates), num + self._neighborhood_radius)
            for neighbor in range(start, end+1):
                if neighbor not in candidates:
                    continue
                distance = abs(neighbor - num) / self._neighborhood_radius
                decay = self._neighbor_decay ** (1 + distance*5)
                heatmap[neighbor] += decay

        # 计算最终权重
        for num in candidates:
            weight = 1.0
            
            # 应用主衰减
            if num in heatmap:
                weight *= self._base_decay ** heatmap[num]
                
            # 应用邻域衰减
            neighbor_effect = sum(
                heatmap.get(n, 0) * (self._neighbor_decay ** (abs(num-n)/10))
                for n in range(num-self._neighborhood_radius,
                             num+self._neighborhood_radius+1)
                if n in candidates and n != num
            )
            weight *= max(0.5, 1 - neighbor_effect * 0.15)
            
            weights[num] = max(weight, self._min_weight)
            
        return weights

    def roll_number(self, candidates):
        """使用权重分布算法滚动随机数"""
        if self.is_rolling and candidates:
            weights = self.calculate_weights(candidates)
            weighted_candidates = list(weights.keys())
            weights_values = list(weights.values())
            
            self.current_number = random.choices(
                population=weighted_candidates,
                weights=weights_values,
                k=1
            )[0]
            
            self.number_label.config(text=str(self.current_number))
            self.master.after(100, lambda: self.roll_number(candidates))

    def record_number(self):
        """记录数字并更新历史窗口"""
        if self.current_number is not None:
            if self.current_number not in self.excluded_numbers:
                # 维护历史窗口
                if len(self.history_window) >= 10:
                    self.history_window.pop(0)
                self.history_window.append(self.current_number)
                
                super().record_number()

    def reset_all(self):
        super().reset_all()
        self.history_window = []


# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    
    # 创建抽奖应用
    # 可以选择不同模式: RandomNumberGenerator, EnhancedRandomNumberGenerator, UniformRandomGenerator
    app = EnhancedRandomNumberGenerator(root)
    
    # 设置窗口大小和位置
    root.geometry("900x600")
    root.minsize(700, 500)
    
    # 设置窗口标题
    root.title("随机数抽奖系统 v2.0")
    
    root.mainloop()