import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import platform

import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from problem.genetic import GeneticAlgorithm
from problem.knapsack import KnapsackProblem


class KnapsackUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Bài toán Cái túi - Genetic Algorithm")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)

        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Scrollable canvas
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Scrollable frame bên trong canvas
        self.scrollable_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Cập nhật vùng scroll khi frame thay đổi kích thước
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Cập nhật chiều rộng canvas window khi resize
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )


        # Bind cuộn chuột cho canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.products = []
        self.selection_options = {"Roulette Wheel Selection" : "roulette", "Tournament Selection" : "tournament", "Random Selection": "random"}
        self.crossover_options = {"Lai một điểm": "one_point", "Lai ngẫu nhiên": "uniform", "Lai hai điểm":"two_points"}
        self.mutation_options = {"Đột biến ngẫu nhiên": "uniform", "Đột biến đảo đoạn": "scramble"}
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.create_widgets()

    def _on_mousewheel(self, event):
        system = platform.system()
        if system == 'Windows':
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        elif system == 'Darwin':  # macOS
            self.canvas.yview_scroll(-1 * int(event.delta), "units")
        else:  # Linux (Button-4, Button-5 đã bind sẵn)
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")


    def create_widgets(self):
        self.build_product_form()
        self.build_product_table()
        self.build_control_buttons()
        self.build_ga_config()

    def build_product_form(self):
        form_frame = tk.Frame(self.scrollable_frame, padx=10, pady=10)
        form_frame.pack(fill="x")
        form_frame.columnconfigure(1, weight=1)

        labels = ["Tên:", "Trọng lượng:", "Giá trị:", "Số lượng tối đa:"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = tk.Entry(form_frame)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=3)
            self.entries[label] = entry

        tk.Button(form_frame, text="Thêm sản phẩm", command=self.add_product).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

   
    def build_product_table(self):
        tree_frame = tk.Frame(self.scrollable_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("number", "name", "weight", "value", "max_quantity")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def build_control_buttons(self):
        self.control_frame = tk.Frame(self.scrollable_frame)
        self.control_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(self.control_frame, text="Xoá sản phẩm", command=self.delete_product).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(self.control_frame, text="Import Excel", command=self.import_excel).grid(row=0, column=1, padx=5, pady=5, sticky="ew")    

    def build_ga_config(self):
        ga_frame = tk.LabelFrame(self.scrollable_frame, text="Cấu hình thuật toán di truyền", padx=10, pady=10)
        ga_frame.pack(fill="x", padx=10, pady=(0, 10))
        ga_frame.columnconfigure(1, weight=1)

        labels = ["Sức chứa túi:", "Số thế hệ:", "Số cá thể:", "Tỷ lệ đột biến:","Tỷ lệ lai tạo:" ,"Số lần chạy:"]
        self.ga_entries = {}

        for i, label in enumerate(labels):
            tk.Label(ga_frame, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = tk.Entry(ga_frame)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=3)
            self.ga_entries[label] = entry

        self.ga_entries["Số lần chạy:"].insert(0, "10")


        tk.Label(ga_frame, text="Kiểu lai:").grid(row=7, column=0, sticky="w", padx=5, pady=3)
        self.crossover_combo = ttk.Combobox(ga_frame, values=list(self.crossover_options.keys()), state="readonly")
        self.crossover_combo.current(0)
        self.crossover_combo.grid(row=7, column=1, sticky="ew", padx=5, pady=3)

        tk.Label(ga_frame, text="Kiểu chọn:").grid(row=8, column=0, sticky="w", padx=5, pady=3)
        self.selection_combo = ttk.Combobox(ga_frame, values=list(self.selection_options.keys()), state="readonly")
        self.selection_combo.current(0)
        self.selection_combo.grid(row=8, column=1, sticky="ew", padx=5, pady=3)  # thêm dòng này để hiển thị combobox selection

        tk.Label(ga_frame, text="Kiểu đột biến:").grid(row=9, column=0, sticky="w", padx=5, pady=3)
        self.mutation_combo = ttk.Combobox(ga_frame, values=list(self.mutation_options.keys()), state="readonly")
        self.mutation_combo.current(0)
        self.mutation_combo.grid(row=9, column=1, sticky="ew", padx=5, pady=3)  # thêm dòng này để hiển thị combobox selection


        tk.Button(ga_frame, text="Chạy thuật toán", command=self.run_ga).grid(row= 10, column=0, columnspan=2, pady=10, sticky="ew")

    def add_product(self):
        try:
            name = self.entries["Tên:"].get()
            weight = float(self.entries["Trọng lượng:"].get())
            value = float(self.entries["Giá trị:"].get())
            max_qty = int(self.entries["Số lượng tối đa:"].get())
            number = len(self.products) + 1
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ.")
            return

        self.products.append({
            "number": number,
            "name": name,
            "weight": weight,
            "value": value,
            "Max_quantity": max_qty
        })
        self.update_table()
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def update_table(self):
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(self.products):
            self.tree.insert("", "end", iid=i, values=(p["number"], p["name"], p["weight"], p["value"], p["Max_quantity"]))

    def delete_product(self):
        selected = self.tree.selection()
        if selected:
            for idx in reversed(selected):
                del self.products[int(idx)]
            self.update_table()
        else:
            messagebox.showwarning("Chọn dòng", "Vui lòng chọn sản phẩm để xoá.")

    def import_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path:
            return
        try:
            df = pd.read_excel(file_path)
            for _, row in df.iterrows():
                number = len(self.products) + 1
                self.products.append({
                    "number": number,
                    "name": row["name"],
                    "weight": float(row["weight"]),
                    "value": float(row["value"]),
                    "Max_quantity": int(row["Max_quantity"])
                })
            self.update_table()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file Excel: {e}")

    def run_ga(self):
        if not self.products:
            messagebox.showerror("Lỗi", "Chưa có sản phẩm.")
            return

        try:
            capacity = float(self.ga_entries["Sức chứa túi:"].get())
            generations = int(self.ga_entries["Số thế hệ:"].get())
            population_size = int(self.ga_entries["Số cá thể:"].get())
            mutation_rate = float(self.ga_entries["Tỷ lệ đột biến:"].get())
            crossover_rate = float(self.ga_entries["Tỷ lệ lai tạo:"].get())
            num_runs = int(self.ga_entries["Số lần chạy:"].get())
            crossover_type = self.crossover_options[self.crossover_combo.get()]
            selection_type = self.selection_options[self.selection_combo.get()]
            mutation_type = self.mutation_options[self.mutation_combo.get()]
        except ValueError:
            messagebox.showerror("Lỗi", "Thông số không hợp lệ.")
            return

        problem = KnapsackProblem(self.products, capacity=capacity) #bài toán cần giải 
        best_logs = []

        for run_idx in range(num_runs): #? lặp nhiều lần để làm gì 
            solver = GeneticAlgorithm(
                problem=problem,
                populationSize=population_size,
                generations=generations,
                crossoverType=crossover_type,
                selectionType=selection_type,
                crossoverRate= crossover_rate,
                mutationType=mutation_type,
                mutationRate=mutation_rate
            )
            logs = solver.run()
            best_gen = max(logs, key=lambda x: x["best"]) # thế hệ tốt nhất của mỗi lần chạy - num_runs 
            best_logs.append((best_gen["best"], run_idx, best_gen, logs))
        for item in best_logs: #debug thế hệ tốt nhất của các lần chạy 
            print(f"{item[0]}, {item[1]}, {item[2]}")

        best_fitness, best_run_idx, best_gen_log, best_run_logs = max(best_logs, key=lambda x: x[0]) # thông số của lần chạy tốt nhất 

        self.show_result_window(problem, population_size, selection_type, mutation_type, generations, crossover_type, mutation_rate, best_gen_log, best_run_logs, best_fitness, best_run_idx, num_runs)

    def show_result_window(self, problem, population_size, selection_type, mutation_type, generations, crossover_type, mutation_rate, best_gen_log, best_run_logs, best_fitness, best_run_idx, num_runs):
        result_window = tk.Toplevel(self.root)
        result_window.title("Biểu đồ thể hiện quy trình tiến hoá")
        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title("Tiến hoá qua các thế hệ")
        ax.set_xlabel("Thế hệ")
        ax.set_ylabel("Fitness")
        ax.grid(True)

        best_line, = ax.plot([], [], label="Best Fitness", color='green')
        avg_line, = ax.plot([], [], label="Average Fitness", color='blue')
        worst_line, = ax.plot([], [], label="Worst Fitness", color='red')
        ax.legend(loc='best')

        canvas = FigureCanvasTkAgg(fig, master=result_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        generations_list, best_list, avg_list, worst_list = [], [], [], []

        def update_chart(log): 
            generations_list.append(log["generation"])
            best_list.append(log["best"])
            avg_list.append(log["avg"])
            worst_list.append(log["worst"])

            best_line.set_data(generations_list, best_list)
            avg_line.set_data(generations_list, avg_list)
            worst_line.set_data(generations_list, worst_list)

            for txt in ax.texts:
                txt.remove()
            # Nếu giá trị fitness tại thế hệ i khác với thế hệ trước hoặc sau 
            # → hiển thị nhãn giá trị ngay trên biểu đồ để người dùng dễ nhìn thấy sự thay đổi bất thường.
            for i in range(1, len(generations_list) - 1):
                for lst, color in [(best_list, 'green'), (avg_list, 'blue'), (worst_list, 'red')]:
                    prev_y, curr_y, next_y = lst[i - 1], lst[i], lst[i + 1]
                    if curr_y != prev_y or curr_y != next_y:
                        ax.annotate(f"{curr_y:.1f}", (generations_list[i], curr_y),
                                    textcoords="offset points", xytext=(0, 5),
                                    ha='center', fontsize=8, color=color)

            ax.relim()
            ax.autoscale_view()
            canvas.draw()
            result_window.update()
            time.sleep(0.1)

        #đưa vào input và gọi thuật toán 
        solver = GeneticAlgorithm(
            problem=problem,
            populationSize=population_size,
            generations=generations,
            selectionType=selection_type,
            mutationType = mutation_type,
            crossoverType=crossover_type,
            mutationRate=mutation_rate
        )
        solver.run(log_callback=update_chart) # nếu callback đc truyền và số thế hệ chia hết cho 10, tức là mỗi sau 10 thế hệ, biểu đồ sẽ được cập nhật lại 

        fig.text(
            0.5, 0.95,
            f"Lần chạy tốt nhất: {best_run_idx + 1}/{num_runs} | Fitness cao nhất: {best_fitness:.2f}",
            ha='center', va='bottom',
            fontsize=10, color='purple', fontweight='bold'
        )
        canvas.draw()

        def show_selected_items():
            item_window = tk.Toplevel(result_window)
            item_window.title("Vật phẩm được chọn - Thế hệ tốt nhất")

            tk.Label(item_window, text="Danh sách vật phẩm được chọn:", font=("Arial", 11, "bold")).pack(pady=5)

            item_tree = ttk.Treeview(item_window, columns=("name", "quantity", "weight", "value"), show="headings")
            for col in ("name", "quantity", "weight", "value"):
                item_tree.heading(col, text=col.capitalize())
            item_tree.pack(fill="both", expand=True, padx=10, pady=5)

            scrollbar = ttk.Scrollbar(item_window, orient="vertical", command=item_tree.yview)
            item_tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

            for i, qty in enumerate(best_gen_log['bestIndividual']):
                if qty > 0:
                    p = self.products[i]
                    item_tree.insert("", "end", values=(p["name"], qty, p["weight"], p["value"]))

        tk.Button(result_window, text="Xem vật phẩm được chọn", command=show_selected_items).pack(pady=(5, 10))

    
     