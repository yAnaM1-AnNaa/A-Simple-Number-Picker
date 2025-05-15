import tkinter as tk
from tkinter import ttk, messagebox
import random
from collections import defaultdict

class RandomNumberGenerator:
    def __init__(self, master):
        self.master = master
        master.title("抽奖")
        
        # 初始化变量
        self.is_rolling = False
        self.excluded_numbers = []
        self.current_number = None
        
        # 创建界面组件
        self.create_widgets()
    
    def create_widgets(self):
        # 参数设置区域
        param_frame = ttk.Frame(self.master, padding=10)
        param_frame.pack(fill=tk.X)
        
        ttk.Label(param_frame, text="最小值:").grid(row=0, column=0, padx=5)
        self.min_entry = ttk.Entry(param_frame, width=8)
        self.min_entry.grid(row=0, column=1, padx=5)
        self.min_entry.insert(0, "100")
        
        ttk.Label(param_frame, text="最大值:").grid(row=0, column=2, padx=5)
        self.max_entry = ttk.Entry(param_frame, width=8)
        self.max_entry.grid(row=0, column=3, padx=5)
        self.max_entry.insert(0, "500")
        
        ttk.Label(param_frame, text="步长:").grid(row=0, column=4, padx=5)
        self.step_entry = ttk.Entry(param_frame, width=8)
        self.step_entry.grid(row=0, column=5, padx=5)
        self.step_entry.insert(0, "1")
        
        # 显示区域
        display_frame = ttk.Frame(self.master, padding=20)
        display_frame.pack()
        
        self.number_label = ttk.Label(
            display_frame, 
            text="", 
            font=('黑体', 52), 
            width=20,
            anchor=tk.CENTER
        )
        self.number_label.pack()
        
        # 控制按钮区域
        button_frame = ttk.Frame(self.master, padding=10)
        button_frame.pack()
        
        self.start_btn = ttk.Button(
            button_frame, 
            text="开始", 
            command=self.toggle_roll,
            width=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.record_btn = ttk.Button(
            button_frame, 
            text="记录", 
            command=self.record_number,
            width=20
        )
        self.record_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = ttk.Button(
            button_frame, 
            text="重置全部", 
            command=self.reset_all,
            width=20
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        # 记录列表区域
        list_frame = ttk.Frame(self.master)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.listbox = tk.Listbox(
            list_frame, 
            height=6,
            selectmode=tk.SINGLE,
            exportselection=False
        )
        scrollbar = ttk.Scrollbar(
            list_frame, 
            orient=tk.VERTICAL, 
            command=self.listbox.yview
        )
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def get_valid_candidates(self):
        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())
            step = int(self.step_entry.get())
            
            if min_val > max_val or step <= 0:
                return None
                
            candidates = list(range(min_val, max_val + 1, step))
            return [num for num in candidates if num not in self.excluded_numbers]
            
        except ValueError:
            return None
    
    def toggle_roll(self):
        if self.is_rolling:
            self.stop_rolling()
        else:
            self.start_rolling()
    
    def start_rolling(self):
        candidates = self.get_valid_candidates()
        
        if not candidates:
            messagebox.showwarning("警告", "没有可用的候选数字！")
            return
            
        self.is_rolling = True
        self.start_btn.config(text="停止")
        self.roll_number(candidates)
    
    def stop_rolling(self):
        self.is_rolling = False
        self.start_btn.config(text="开始")
    
    def roll_number(self, candidates):
        if self.is_rolling and candidates:
            self.current_number = random.choice(candidates)
            self.number_label.config(text=str(self.current_number))
            self.master.after(12, lambda: self.roll_number(candidates))
    
    def record_number(self):
        if self.current_number is not None:
            if self.current_number not in self.excluded_numbers:
                self.excluded_numbers.append(self.current_number)
                self.update_list_display()  # 改为调用更新方法
                self.current_number = None
                self.number_label.config(text="已记录")
                self.is_rolling = False
                self.start_btn.config(text="开始")
    
    def reset_all(self):
        self.stop_rolling()
        self.excluded_numbers = []
        self.listbox.delete(0, tk.END)
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, "100")
        self.max_entry.delete(0, tk.END)
        self.max_entry.insert(0, "500")
        self.step_entry.delete(0, tk.END)
        self.step_entry.insert(0, "1")
        self.number_label.config(text="")

class EnhancedRandomNumberGenerator(RandomNumberGenerator):
    def __init__(self, master):
        super().__init__(master)
        
        # 增加手动添加和撤销组件
        self.create_additional_widgets()

    def update_list_display(self):
        """更新列表框显示带序号的记录"""
        self.listbox.delete(0, tk.END)  # 清空现有列表
        # 重新插入带序号的记录
        for idx, num in enumerate(self.excluded_numbers, start=1):
            self.listbox.insert(tk.END, f"{idx}. {num}")
    
    def create_additional_widgets(self):
        # 手动添加和撤销区域
        add_remove_frame = ttk.Frame(self.master, padding=10)
        add_remove_frame.pack(fill=tk.X)
        
        ttk.Label(add_remove_frame, text="手动添加:").pack(side=tk.LEFT, padx=5)
        self.manual_entry = ttk.Entry(add_remove_frame, width=8)
        self.manual_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            add_remove_frame, 
            text="添加", 
            command=self.manual_add,
            width=8
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            add_remove_frame, 
            text="↩撤销", 
            command=self.undo_record,
            width=8
        ).pack(side=tk.LEFT, padx=5)

    def manual_add(self):
        num_str = self.manual_entry.get()
        if not num_str:
            return
            
        try:
            num = int(num_str)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数")
            return
            
        if num in self.excluded_numbers:
            messagebox.showwarning("警告", "该数字已被排除")
            return
            
        self.excluded_numbers.append(num)
        self.update_list_display()  # 改为调用更新方法
        self.manual_entry.delete(0, tk.END)
        messagebox.showinfo("成功", f"已添加 {num} 到排除列表")

    def undo_record(self):
        if self.excluded_numbers:
            removed_num = self.excluded_numbers.pop()
            self.update_list_display()  # 改为调用更新方法
            messagebox.showinfo("撤销成功", f"已撤销数字 {removed_num}")
        else:
            messagebox.showinfo("提示", "没有可撤销的记录")

    # 修改原有重置方法
    def reset_all(self):
        super().reset_all()
        self.update_list_display()  # 确保重置后显示正确

class UniformRandomGenerator(RandomNumberGenerator):
    def __init__(self, master):
        super().__init__(master)
        
        # 固定邻域参数配置
        self._neighborhood_radius = 75      # 邻域影响半径
        self._base_decay = 0.38             # 主衰减系数
        self._neighbor_decay = 0.85        # 邻域衰减系数
        self._min_weight = 0.18             # 最小权重限制
        
        # 历史记录窗口
        self.history_window = []

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

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedRandomNumberGenerator(root)
    root.geometry("500x500")
    root.mainloop()