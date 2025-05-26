import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import threading
import numpy as np
from problem.knapsack import KnapsackProblem
from problem.genetic import GeneticAlgorithm

class HistogramGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Histogram Fitness Cao Nhất với GA Knapsack")
        self.geometry("900x650")

        self.problem = None
        self.max_generations = 100
        self.max_population = 100
        # Tham số khảo sát và dãy giá trị tương ứng
        self.params = {
            "Generations": list(range(10, self.max_generations, 10)),
            "Population Size": list(range(20, self.max_population, 10)),
            "Crossover Rate": [i / 10 for i in range(0, 11)],   # 0.0, 0.1, ..., 1.0
            "Mutation Rate": [i / 20 for i in range(0, 21)],   # 0.0, 0.05, ..., 1.0
            "Runs": list(range(10, 200))  # khảo sát số lần chạy từ 1 đến 20 lần
        }

        self.create_widgets()
        self.figure, self.ax = plt.subplots(figsize=(7, 4))

    def create_widgets(self):
        frame_top = ttk.Frame(self)
        frame_top.pack(fill=tk.X, padx=10, pady=5)

        btn_load = ttk.Button(frame_top, text="Load file Excel chứa bài toán", command=self.load_excel)
        btn_load.pack(side=tk.LEFT)

        self.lbl_file = ttk.Label(frame_top, text="Chưa có file nào được tải")
        self.lbl_file.pack(side=tk.LEFT, padx=10)

        ttk.Label(frame_top, text="Capacity:").pack(side=tk.LEFT, padx=(20,5))
        self.entry_capacity = ttk.Entry(frame_top, width=8)
        self.entry_capacity.pack(side=tk.LEFT)

        frame_params = ttk.Frame(self)
        frame_params.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_params, text="Chọn tham số khảo sát:").pack(side=tk.LEFT)

        self.param_combo = ttk.Combobox(frame_params, values=list(self.params.keys()), state='readonly')
        self.param_combo.current(0)
        self.param_combo.pack(side=tk.LEFT, padx=5)

        self.btn_run = ttk.Button(frame_params, text="Chạy khảo sát", command=self.run_survey)
        self.btn_run.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_params, text="Generations:").pack(side=tk.LEFT, padx=5)

        self.entry_generations = ttk.Entry(frame_params, width=5)
        self.entry_generations.insert(0, "50")
        self.entry_generations.pack(side=tk.LEFT)

        ttk.Label(frame_params, text="Population:").pack(side=tk.LEFT, padx=5)
        self.entry_population = ttk.Entry(frame_params, width=5)
        self.entry_population.insert(0, "50")
        self.entry_population.pack(side=tk.LEFT)

        ttk.Label(frame_params, text="Crossover:").pack(side=tk.LEFT, padx=5)
        self.entry_crossover = ttk.Entry(frame_params, width=5)
        self.entry_crossover.insert(0, "0.8")
        self.entry_crossover.pack(side=tk.LEFT)

        ttk.Label(frame_params, text="Mutation:").pack(side=tk.LEFT, padx=5)
        self.entry_mutation = ttk.Entry(frame_params, width=5)
        self.entry_mutation.insert(0, "0.05")
        self.entry_mutation.pack(side=tk.LEFT)

        ttk.Label(frame_params, text="Runs:").pack(side=tk.LEFT, padx=5)
        self.entry_runs = ttk.Entry(frame_params, width=5)
        self.entry_runs.insert(0, "100")
        self.entry_runs.pack(side=tk.LEFT)

        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_excel(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")],
            title="Chọn file Excel chứa dữ liệu bài toán Knapsack"
        )
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            required_cols = {'name', 'weight', 'value', 'Max_quantity'}
            if not required_cols.issubset(set(df.columns)):
                messagebox.showerror("Lỗi", f"File Excel phải chứa các cột: {required_cols}")
                return

            items = df.to_dict(orient='records')

            self.problem = KnapsackProblem(items, capacity=1)
            self.lbl_file.config(text=f"Đã tải file: {file_path.split('/')[-1]}")
            messagebox.showinfo("Thành công", "Đã tải bài toán từ file Excel thành công!")

        except Exception as e:
            messagebox.showerror("Lỗi khi đọc file", str(e))

    def run_survey(self):
        try:
            self.max_generations = int(self.entry_generations.get())
            self.max_population = int(self.entry_population.get())
            if self.max_generations < 10 or self.max_population < 20:
                raise ValueError
        except Exception:
            messagebox.showerror("Lỗi nhập liệu", "Max Generations phải >=10, Max Population phải >=20 và là số nguyên.")
            return
        
        self.params["Generations"] = list(range(10, self.max_generations + 1, 10))
        self.params["Population Size"] = list(range(20, self.max_population + 1, 10))

        if self.problem is None:
            messagebox.showwarning("Chưa tải bài toán", "Vui lòng tải file Excel bài toán trước khi chạy khảo sát.")
            return

        try:
            capacity = int(self.entry_capacity.get())
            if capacity <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Lỗi nhập liệu", "Capacity phải là số nguyên dương.")
            return

        self.problem.capacity = capacity

        self.btn_run.config(state=tk.DISABLED)

        threading.Thread(target=self._run_survey_thread).start()

   
    def _run_survey_thread(self):
        param_name = self.param_combo.get()
        values = self.params[param_name]
        print(f"Đang khảo sát với {param_name} giá trị: {values}")

        fitness_counter = Counter()

        try:
            fixed_params = {
                "generations": int(self.entry_generations.get()),
                "populationSize": int(self.entry_population.get()),
                "crossoverType": "uniform",
                "selectionType": "tournament",
                "mutationType": "uniform",
                "crossoverRate": float(self.entry_crossover.get()),
                "mutationRate": float(self.entry_mutation.get()),
                "runs": int(self.entry_runs.get())
            }
        except Exception:
            self.after(0, messagebox.showerror, "Lỗi nhập liệu", "Vui lòng nhập đúng định dạng số cho các tham số.")
            self.after(0, lambda: self.btn_run.config(state=tk.NORMAL))
            return

        try:
            for v in values:
                param_settings = fixed_params.copy()
                if param_name == "Generations":
                    param_settings["generations"] = v
                elif param_name == "Population Size":
                    param_settings["populationSize"] = v
                elif param_name == "Crossover Rate":
                    param_settings["crossoverRate"] = v
                elif param_name == "Mutation Rate":
                    param_settings["mutationRate"] = v
                elif param_name == "Runs":
                    param_settings["runs"] = v

                all_best_fitnesses = []

                for _ in range(param_settings["runs"]):
                    ga = GeneticAlgorithm(
                        problem=self.problem,
                        populationSize=param_settings["populationSize"],
                        generations=param_settings["generations"],
                        crossoverType=param_settings["crossoverType"],
                        selectionType=param_settings["selectionType"],
                        mutationType=param_settings["mutationType"],
                        crossoverRate=param_settings["crossoverRate"],
                        mutationRate=param_settings["mutationRate"],
                    )
                    logs = ga.run()
                    best_fitnesses = [log['best'] for log in logs]
                    all_best_fitnesses.append(best_fitnesses)

                min_len = min(len(run) for run in all_best_fitnesses)
                avg_fitness = sum([max(run[:min_len]) for run in all_best_fitnesses]) / param_settings["runs"]
                fitness_threshold = avg_fitness * 1.1

                count_over_threshold = 0
                for run in all_best_fitnesses:
                    if max(run[:min_len]) > fitness_threshold:
                        count_over_threshold += 1

                fitness_counter[v] = count_over_threshold

            self.after(0, self.plot_histogram, fitness_counter, param_name)

        except Exception as e:
            self.after(0, messagebox.showerror, "Lỗi khi chạy khảo sát", str(e))

        self.after(0, lambda: self.btn_run.config(state=tk.NORMAL))


    def plot_histogram(self, counter, param_name):
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
            del self.canvas

        fig, ax = plt.subplots(figsize=(7, 4))

        x = np.array(list(counter.keys()))
        y = np.array(list(counter.values()))

        # Chọn số bin (khoảng) cho histogram
        num_bins = 8  # Bạn có thể thay đổi số bin này cho phù hợp

        # Tạo các biên bin từ min đến max giá trị x
        bins = np.linspace(x.min(), x.max(), num_bins + 1)

        # Tạo mảng lưu tổng số lần fitness vượt ngưỡng trong mỗi bin
        bin_sums = np.zeros(num_bins)

        # Gán từng giá trị vào bin và cộng giá trị y tương ứng
        for xi, yi in zip(x, y):
            bin_idx = np.digitize(xi, bins) - 1
            # Giới hạn bin_idx trong khoảng 0 đến num_bins-1
            bin_idx = min(max(bin_idx, 0), num_bins - 1)
            bin_sums[bin_idx] += yi

        # Tính trung điểm của mỗi bin để vẽ
        bin_centers = (bins[:-1] + bins[1:]) / 2

        # Vẽ bar với chiều rộng gần bằng khoảng bin
        ax.bar(bin_centers, bin_sums, width=(bins[1] - bins[0]) * 0.9, color='skyblue')

        ax.set_title(f"Số lần fitness > ngưỡng theo tham số: {param_name} (theo khoảng)")
        ax.set_xlabel(param_name)
        ax.set_ylabel("Số lần fitness vượt ngưỡng")
        ax.grid(True)

        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)