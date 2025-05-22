import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from problem.knapsack import KnapsackProblem
from problem.genetic import GeneticAlgorithm  # module bạn đã viết ở trên
import threading


class GAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GA Knapsack - Nhiều lần chạy với tham số biến đổi")

        self.problem = None
        self.products = []
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Các input
        labels = ["Capacity", "Population Size", "Generations", "Crossover Rate", "Mutation Rate", "Runs"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame, text=label).grid(row=0, column=i)
            entry = tk.Entry(frame, width=8)
            entry.grid(row=1, column=i)
            self.entries[label] = entry

        options = {
            "Crossover Type": ['one_point', 'two_points', 'uniform'],
            "Selection Type": ['tournament', 'random', 'roulette'],
            "Mutation Type": ['uniform', 'scramble']
        }
        self.comboboxes = {}
        for i, (label, values) in enumerate(options.items()):
            tk.Label(frame, text=label).grid(row=2, column=i)
            combobox = ttk.Combobox(frame, values=values, state="readonly", width=10)
            combobox.current(0)
            combobox.grid(row=3, column=i)
            self.comboboxes[label] = combobox

        # Loại biến đổi tham số
        tk.Label(frame, text="Parameter Change Mode").grid(row=0, column=len(labels))
        self.change_mode = ttk.Combobox(frame, values=['increase', 'decrease', 'random'], state="readonly", width=10)
        self.change_mode.current(0)
        self.change_mode.grid(row=1, column=len(labels))

        # Tham số muốn thay đổi
        tk.Label(frame, text="Param to Change").grid(row=2, column=len(labels))
        self.param_to_change = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=0, height=3)
        for param in ["Population Size", "Generations", "Crossover Rate", "Mutation Rate"]:
            self.param_to_change.insert(tk.END, param)
        self.param_to_change.grid(row=3, column=len(labels))

        # Nút load excel + run
        tk.Button(frame, text="Load Excel", command=self.load_excel).grid(row=1, column=len(labels)+1, padx=5)
        tk.Button(frame, text="Run Experiments", command=self.run_experiments).grid(row=3, column=len(labels)+1, padx=5)

        # Vùng hiển thị danh sách vật phẩm
        self.product_table = tk.Text(self.root, height=8, width=80)
        self.product_table.pack(pady=5)

        # Biểu đồ
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack()

        # Log text
        self.log_text = tk.Text(self.root, height=10)
        self.log_text.pack()

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

            param_mode = self.change_mode.get()
            selected_indices = self.param_to_change.curselection()
            params_to_change = [self.param_to_change.get(i) for i in selected_indices]

            self.problem = KnapsackProblem( self.products, capacity=capacity)

            self.ax.clear()
            self.log_text.delete(1.0, tk.END)
            threading.Thread(target=self.run_trials, args=(base_params, runs, params_to_change, param_mode)).start()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Chưa nhập đủ dữ liệu: {e}")

    def run_trials(self, base_params, runs, params_to_change, mode):
        results = []
        crossover_type = self.comboboxes["Crossover Type"].get()
        selection_type = self.comboboxes["Selection Type"].get()
        mutation_type = self.comboboxes["Mutation Type"].get()

        for run in range(1, runs + 1):
            params = base_params.copy()
            for p in params_to_change:
                if p == "Population Size":
                    params["pop_size"] = self.modify_value(params["pop_size"], mode, 10, 200)
                elif p == "Generations":
                    params["generations"] = self.modify_value(params["generations"], mode, 10, 300)
                elif p == "Crossover Rate":
                    params["crossover_rate"] = self.modify_value(params["crossover_rate"], mode, 0.3, 1.0, 0.05)
                elif p == "Mutation Rate":
                    params["mutation_rate"] = self.modify_value(params["mutation_rate"], mode, 0.01, 0.3, 0.01)

            ga = GeneticAlgorithm(
                self.problem, params["pop_size"], params["generations"],
                crossover_type, selection_type, mutation_type,
                params["crossover_rate"], params["mutation_rate"]
            )
            logs = ga.run()
            best_fitness = max(log["best"] for log in logs)
            results.append(best_fitness)

            self.log_text.insert(tk.END, f"Run {run}: Best fitness = {best_fitness}\n")
            self.log_text.see(tk.END)

        self.ax.plot(range(1, runs+1), results, marker='o')
        self.ax.set_title("Best Fitness qua các lần chạy")
        self.ax.set_xlabel("Run")
        self.ax.set_ylabel("Best Fitness")
        self.ax.grid(True)
        self.canvas.draw()

    def modify_value(self, value, mode, min_val, max_val, step=5):
        if mode == 'increase':
            new_value = value + step
            return min(new_value, max_val)
        elif mode == 'decrease':
            new_value = value - step
            return max(new_value, min_val)
        elif mode == 'random':
            if isinstance(value, float):
                return round(random.uniform(min_val, max_val), 2)
            else:
                return random.randint(min_val, max_val)
        else:
            return value
