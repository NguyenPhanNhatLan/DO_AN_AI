import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from problem.knapsack import KnapsackProblem
from problem.genetic import GeneticAlgorithm
import threading


class GAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GA Knapsack - Nhiều lần chạy với tham số biến đổi")

        self.problem = None
        self.products = []
        self.create_widgets()

    def create_widgets(self):
        # Frame đầu vào thu gọn và chia cột
        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        labels = ["Capacity", "Population Size", "Generations", "Crossover Rate", "Mutation Rate", "Runs"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(input_frame, text=label, font=("TkDefaultFont", 8)).grid(row=0, column=i)
            entry = tk.Entry(input_frame, width=8)
            entry.grid(row=1, column=i)
            self.entries[label] = entry

        options = {
            "Crossover Type": ['one_point', 'two_points', 'uniform'],
            "Selection Type": ['tournament', 'random', 'roulette'],
            "Mutation Type": ['uniform', 'scramble']
        }
        self.comboboxes = {}
        for i, (label, values) in enumerate(options.items()):
            tk.Label(input_frame, text=label, font=("TkDefaultFont", 8)).grid(row=2, column=i)
            combobox = ttk.Combobox(input_frame, values=values, state="readonly", width=10)
            combobox.current(0)
            combobox.grid(row=3, column=i)
            self.comboboxes[label] = combobox

        # Cột riêng cho các thành phần phụ
        tk.Label(input_frame, text="Parameter Change Mode", font=("TkDefaultFont", 8)).grid(row=0, column=len(labels))
        self.change_mode = ttk.Combobox(input_frame, values=['increase', 'decrease'], state="readonly", width=10)
        self.change_mode.current(0)
        self.change_mode.grid(row=1, column=len(labels))

        tk.Label(input_frame, text="Param to Change", font=("TkDefaultFont", 8)).grid(row=2, column=len(labels))
        self.param_to_change = tk.Listbox(input_frame, selectmode=tk.MULTIPLE, exportselection=0, height=3)
        for param in ["Population Size", "Generations", "Crossover Rate", "Mutation Rate"]:
            self.param_to_change.insert(tk.END, param)
        self.param_to_change.grid(row=3, column=len(labels))

        tk.Button(input_frame, text="Load Excel", command=self.load_excel).grid(row=1, column=len(labels)+1, padx=5)
        tk.Button(input_frame, text="Run Experiments", command=self.run_experiments).grid(row=3, column=len(labels)+1, padx=5)

        # Tabs bên dưới chiếm toàn bộ không gian còn lại
        tab_control = ttk.Notebook(self.root)
        tab_control.pack(fill=tk.BOTH, expand=True)

        result_tab = tk.Frame(tab_control)
        tab_control.add(result_tab, text='Kết quả')

        self.product_table = tk.Text(result_tab, height=8, width=80)
        self.product_table.pack(pady=5, fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(result_tab, height=10)
        self.log_text.pack(pady=5, fill=tk.BOTH, expand=True)

        plot_tab = tk.Frame(tab_control)
        tab_control.add(plot_tab, text='Biểu đồ')

        self.figure, self.ax = plt.subplots(figsize=(16, 6))
        self.ax.tick_params(labelsize=8)  # Giảm kích thước chữ của trục
        self.ax.title.set_fontsize(10)    # Giảm kích thước tiêu đề nếu có
        self.ax.xaxis.label.set_size(9)   # Kích thước nhãn trục X
        self.ax.yaxis.label.set_size(9)   # Kích thước nhãn trục Y

        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_tab)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Button(self.root, text="📈 Mở Biểu Đồ Rộng", command=self.open_fullscreen_plot).pack(pady=5)

    def load_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return
        try:
            df = pd.read_excel(file_path)
            self.products.clear()
            for _, row in df.iterrows():
                number = len(self.products) + 1
                self.products.append({
                    "number": number,
                    "name": row["name"],
                    "weight": float(row["weight"]),
                    "value": float(row["value"]),
                    "Max_quantity": int(row["Max_quantity"])
                })

            self.product_table.delete(1.0, tk.END)
            for item in self.products:
                line = f"{item['number']}. {item['name']} - W:{item['weight']} - V:{item['value']} - Max:{item['Max_quantity']}\n"
                self.product_table.insert(tk.END, line)
            messagebox.showinfo("✅ Thành công", f"Đã load {len(self.products)} sản phẩm.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không đọc được file Excel: {e}")

    def run_experiments(self):
        try:
            capacity = int(self.entries["Capacity"].get())
            base_params = {
                "pop_size": int(self.entries["Population Size"].get()),
                "generations": int(self.entries["Generations"].get()),
                "crossover_rate": float(self.entries["Crossover Rate"].get()),
                "mutation_rate": float(self.entries["Mutation Rate"].get())
            }
            runs = int(self.entries["Runs"].get())
            self.runs = runs  # Lưu runs để dùng ở hàm khác

            param_mode = self.change_mode.get()
            selected_indices = self.param_to_change.curselection()
            params_to_change = [self.param_to_change.get(i) for i in selected_indices] 


            self.problem = KnapsackProblem(self.products, capacity=capacity)

            self.ax.clear()
            self.log_text.delete(1.0, tk.END)
            self.canvas.draw()

            threading.Thread(
                target=self.run_trials,
                args=(base_params, runs, params_to_change, param_mode),
                daemon=True
            ).start()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Chưa nhập đủ dữ liệu: {e}")

    def run_trials(self, base_params, runs, params_to_change, mode):
        self.ax.clear()

        if len(params_to_change) > 1:
            messagebox.showerror("Lỗi", "Vui lòng chỉ chọn tối đa 1 tham số để thay đổi.")
            return

        params = base_params.copy()
        results = []
        run_numbers = []

        for run in range(1, runs + 1):
            label_info = ""

            if len(params_to_change) == 1:
                param_to_change = params_to_change[0]
                if param_to_change == "Population Size":
                    params["pop_size"] = self.modify_value(params["pop_size"], mode, 10, 10000)
                    label_info = f" | Pop Size: {params['pop_size']}"
                elif param_to_change == "Generations":
                    params["generations"] = self.modify_value(params["generations"], mode, 10, 10000)
                    label_info = f" | Generations: {params['generations']}"
                elif param_to_change == "Crossover Rate":
                    params["crossover_rate"] = self.modify_value(params["crossover_rate"], mode, 0.3, 1.0, run - 1)
                    label_info = f" | Crossover Rate: {params['crossover_rate']:.2f}"
                elif param_to_change == "Mutation Rate":
                    params["mutation_rate"] = self.modify_value(params["mutation_rate"], mode, 0.01, 1.0, run - 1)
                    label_info = f" | Mutation Rate: {params['mutation_rate']:.2f}"

            ga = GeneticAlgorithm(
                self.problem,
                params["pop_size"],
                params["generations"],
                self.comboboxes["Crossover Type"].get(),
                self.comboboxes["Selection Type"].get(),
                self.comboboxes["Mutation Type"].get(),
                params["crossover_rate"],
                params["mutation_rate"]
            )
            logs = ga.run()
            best_fitness = max(float(log["best"]) for log in logs)

            results.append(best_fitness)
            run_numbers.append(run)
            self.log_text.insert(tk.END, f"[Run {run}]{label_info} → Best fitness = {best_fitness}\n")
            self.log_text.see(tk.END)

        self.ax.plot(run_numbers, results, label="Best Fitness", linewidth=2.0, marker='o', color='blue')
        self.ax.set_title("Best Fitness qua các lần chạy")
        self.ax.set_xlabel("Số lần chạy")
        self.ax.set_ylabel("Best Fitness")
        self.ax.grid(True, linestyle='--', linewidth=0.5)
        self.ax.legend(fontsize=8)
        self.canvas.draw()

    def modify_value(self, value, mode, min_val, max_val, run_index=0):
        total_steps = self.runs - 1  # tránh chia cho 0 nếu runs=1
    
        if isinstance(value, float):
            total_steps = self.runs - 1
            step = (max_val - min_val) / total_steps if total_steps else 0
            if mode == 'increase':
                return min(min_val + step * run_index, max_val)
            elif mode == 'decrease':
                return max(max_val - step * run_index, min_val)
            else:
                return value
        else:
            # Int: tăng giảm 5 mỗi lần, không cần run_index
            if mode == 'increase':
                return min(value + 5, max_val)
            elif mode == 'decrease':
                return max(value - 5, min_val)
            else:
                return value
    def open_fullscreen_plot(self):
        import tkinter as tk
        from tkinter import ttk
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        # Tạo cửa sổ popup mới
        popup = tk.Toplevel(self.root)
        popup.title("Biểu đồ thể hiện quy trình tiến hoá")
        popup.geometry("800x600")
        popup.configure(bg="white")

        # Label tiêu đề lớn
        title_text = f"Lần chạy tốt nhất: {self.best_run_index + 1}/{self.runs} | Fitness cao nhất: {self.best_run_fitness:.2f}"
        tk.Label(popup, text=title_text, font=("Helvetica", 14, "bold"), fg="purple", bg="white").pack(pady=(10, 0))
        tk.Label(popup, text="Tiến hoá qua các thế hệ", font=("Helvetica", 12), bg="white").pack(pady=(0, 10))

        # Tạo biểu đồ matplotlib riêng
        fig, ax = plt.subplots(figsize=(8, 4))
        generations = list(range(1, len(self.best_fitness_per_gen) + 1))

        ax.plot(generations, self.best_fitness_per_gen, label="Best Fitness", color="green")
        ax.plot(generations, self.avg_fitness_per_gen, label="Average Fitness", color="blue")
        ax.plot(generations, self.worst_fitness_per_gen, label="Worst Fitness", color="red")

        ax.set_xlabel("Thế hệ")
        ax.set_ylabel("Fitness")
        ax.grid(True)
        ax.legend()

        # Vẽ số lên từng đường (chọn vài điểm chính)
        for arr, color in [
            (self.best_fitness_per_gen, "green"),
            (self.avg_fitness_per_gen, "blue"),
            (self.worst_fitness_per_gen, "red"),
        ]:
            for i in [10, 50, 90]:  # hoặc tùy chọn điểm nổi bật
                if i < len(arr):
                    ax.text(i, arr[i], f"{arr[i]:.1f}", fontsize=8, color=color)

        # Gắn matplotlib vào tkinter
        canvas = FigureCanvasTkAgg(fig, master=popup)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Nút tương tác phía dưới
        ttk.Button(popup, text="Xem vật phẩm được chọn", command=self.show_selected_items_popup).pack(pady=10)