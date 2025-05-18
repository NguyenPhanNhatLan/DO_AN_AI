import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from problem.genetic import GeneticAlgorithm
from problem.knapsack import KnapsackProblem


def start():
    products = []
    def add_product():
        number = len(products) + 1
        name = name_entry.get()
        try:
            weight = float(weight_entry.get())
            value = float(value_entry.get())
            max_qty = int(max_qty_entry.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ.")
            return
        products.append({"number": number ,"name": name, "weight": weight, "value": value, "Max_quantity": max_qty})
        update_table()
        name_entry.delete(0, tk.END)
        weight_entry.delete(0, tk.END)
        value_entry.delete(0, tk.END)
        max_qty_entry.delete(0, tk.END)

    def update_table():
        for row in tree.get_children():
            tree.delete(row)
        for i, p in enumerate(products):
            tree.insert("", "end", iid=i, values=(p["number"], p["name"], p["weight"], p["value"], p["Max_quantity"]))

    def delete_product():
        selected = tree.selection()
        if selected:
            for idx in reversed(selected):
                del products[int(idx)]
            update_table()
        else:
            messagebox.showwarning("Chọn dòng", "Vui lòng chọn sản phẩm để xoá.")

    def import_excel():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            try:
                df = pd.read_excel(file_path)
                for _, row in df.iterrows():
                    number = len(products) + 1
                    products.append({
                        "number": number,
                        "name": row["name"],
                        "weight": float(row["weight"]),
                        "value": float(row["value"]),
                        "Max_quantity": int(row["Max_quantity"])
                    })
                update_table()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file Excel: {e}")

    def run_ga():
        if not products:
            messagebox.showerror("Lỗi", "Chưa có sản phẩm.")
            return
        
        try:
            capacity = float(capacity_entry.get())
            generations = int(generations_entry.get())
            population_size = int(pop_size_entry.get())
            mutation_rate = float(mutation_rate_entry.get())
            selected = crossover_combo.get()
            crossover_type = crossover_options[selected]
            num_runs = int(num_runs_entry.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Thông số không hợp lệ.")
            return

        problem = KnapsackProblem(products, capacity=capacity)

        # Tạo cửa sổ kết quả realtime
        result_window = tk.Toplevel(root)
        result_window.title("Tiến hoá realtime")

        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title("Tiến hoá qua các thế hệ")
        ax.set_xlabel("Thế hệ")
        ax.set_ylabel("Fitness")
        ax.grid(True)

        best_line, = ax.plot([], [], label="Best Fitness", color='green')
        avg_line, = ax.plot([], [], label="Average Fitness", color='blue')
        worst_line, = ax.plot([], [], label="Worst Fitness", color='red')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))


        canvas = FigureCanvasTkAgg(fig, master=result_window)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Danh sách log dữ liệu
        generations_list, best_list, avg_list, worst_list = [], [], [], []

        def update_chart(log):
            generations_list.append(log["generation"])
            best_list.append(log["best"])
            avg_list.append(log["avg"])
            worst_list.append(log["worst"])

            best_line.set_data(generations_list, best_list)
            avg_line.set_data(generations_list, avg_list)
            worst_line.set_data(generations_list, worst_list)

            # Xóa annotation cũ trước khi vẽ cái mới
            for txt in ax.texts:
                txt.remove()

            # Chỉ annotate các điểm gấp khúc
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
            time.sleep(0.5)


        # Chạy GA nhiều lần, không realtime
        all_run_logs = []
        best_per_run = []
        for run_idx in range(num_runs):
            solver = GeneticAlgorithm(
                problem=problem,
                populationSize=population_size,
                generations=generations,
                crossoverType=crossover_type,
                mutationRate=mutation_rate
            )
            logs = solver.run()
            all_run_logs.append(logs)
            best_gen_log = max(logs, key=lambda x: x['best'])
            best_per_run.append((best_gen_log['best'], run_idx, best_gen_log, logs))

        # Tìm lần chạy tốt nhất
        best_overall_fitness, best_run_idx, best_gen_log, best_run_logs = max(best_per_run, key=lambda x: x[0])

        # Reset dữ liệu chart
        generations_list.clear()
        best_list.clear()
        avg_list.clear()
        worst_list.clear()

        # Chạy lại lần tốt nhất với realtime
        solver = GeneticAlgorithm(
            problem=problem,
            populationSize=population_size,
            generations=generations,
            crossoverType=crossover_type,
            mutationRate=mutation_rate
        )
        solver.run(log_callback=update_chart)

        messagebox.showinfo("Hoàn tất", f"Lần chạy tốt nhất: {best_run_idx + 1}/{num_runs}\nFitness cao nhất: {best_overall_fitness:.2f}")


    def plot_chart(run_index, num_runs, best_fitness_value, best_individual, logs):
        generations   = [log["generation"] for log in logs]
        best_fitness  = [log["best"]       for log in logs]
        avg_fitness   = [log["avg"]        for log in logs]
        worst_fitness = [log["worst"]      for log in logs]

        result_window = tk.Toplevel(root)
        result_window.title("Kết quả tiến hoá")

        info_lbl = tk.Label(
            result_window,
            text=f"Lần chạy tốt nhất: {run_index}/{num_runs} | Fitness cao nhất: {best_fitness_value:.2f}",
            font=("Arial", 11, "bold"),
            fg="blue"
        )
        info_lbl.pack(pady=(10, 0))

        fig = Figure(figsize=(7, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(generations, best_fitness, label="Best Fitness", color='green')
        ax.plot(generations, avg_fitness, label="Average Fitness", color='blue')
        ax.plot(generations, worst_fitness, label="Worst Fitness", color='red')
        ax.set_title("Tiến hoá qua các thế hệ")
        ax.set_xlabel("Thế hệ")
        ax.set_ylabel("Fitness")
        ax.legend()
        ax.grid(True)

        chart_frame = tk.Frame(result_window)
        chart_frame.pack(fill="both", expand=False, padx=10, pady=5)
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        table_frame = tk.Frame(result_window)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk.Label(table_frame, text="Vật phẩm được chọn:", font=("Arial", 10, "bold")).pack(anchor="w")

        result_tree = ttk.Treeview(table_frame, columns=("name", "quantity"), show="headings", height=10)
        result_tree.heading("name", text="Tên vật phẩm")
        result_tree.heading("quantity", text="Số lượng được chọn")
        result_tree.column("name", anchor="center")
        result_tree.column("quantity", anchor="center")
        result_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=result_tree.yview)
        result_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        for i, qty in enumerate(best_individual):
            if qty > 0:
                result_tree.insert("", "end", values=(products[i]["name"], qty))

        def save_results():
            file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file:
                selected_items = []
                for i, qty in enumerate(best_individual):
                    if qty > 0:
                        selected_items.append({
                            "name": products[i]["name"],
                            "quantity": qty,
                            "weight": products[i]["weight"],
                            "value": products[i]["value"]
                        })
                pd.DataFrame(selected_items).to_excel(file, index=False)
                messagebox.showinfo("Thành công", "Đã lưu kết quả.")

        save_btn = tk.Button(result_window, text="Lưu kết quả ra Excel", command=save_results)
        save_btn.pack(pady=(0, 10))


    root = tk.Tk()
    root.title("Bài toán Cái túi - Genetic Algorithm")

    form_frame = tk.Frame(root, padx=10, pady=10)
    form_frame.pack(fill="x", expand=False)
    form_frame.columnconfigure(1, weight=1)

    tk.Label(form_frame, text="Tên:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
    name_entry = tk.Entry(form_frame)
    name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(form_frame, text="Trọng lượng:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
    weight_entry = tk.Entry(form_frame)
    weight_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(form_frame, text="Giá trị:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
    value_entry = tk.Entry(form_frame)
    value_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(form_frame, text="Số lượng tối đa:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
    max_qty_entry = tk.Entry(form_frame)
    max_qty_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=3)

    add_button = tk.Button(form_frame, text="Thêm sản phẩm", command=add_product)
    add_button.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

    tree_frame = tk.Frame(root)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    tree = ttk.Treeview(tree_frame, columns=("number", "name", "weight", "value", "max_quantity"), show="headings", height=8)
    for col in ("number","name", "weight", "value", "max_quantity"):
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=100, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    control_frame = tk.Frame(root)
    control_frame.pack(pady=(0, 10))
    tk.Button(control_frame, text="Xoá sản phẩm", command=delete_product).pack(side="left", padx=5)
    tk.Button(control_frame, text="Import Excel", command=import_excel).pack(side="left", padx=5)

    ga_frame = tk.LabelFrame(root, text="Cấu hình thuật toán di truyền", padx=10, pady=10)
    ga_frame.pack(fill="x", padx=10, pady=(0, 10))
    ga_frame.columnconfigure(1, weight=1)

    tk.Label(ga_frame, text="Sức chứa túi:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
    capacity_entry = tk.Entry(ga_frame)
    capacity_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(ga_frame, text="Số thế hệ:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
    generations_entry = tk.Entry(ga_frame)
    generations_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(ga_frame, text="Số cá thể:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
    pop_size_entry = tk.Entry(ga_frame)
    pop_size_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(ga_frame, text="Tỷ lệ đột biến:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
    mutation_rate_entry = tk.Entry(ga_frame)
    mutation_rate_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(ga_frame, text="Số lần chạy:").grid(row=4, column=0, sticky="w", padx=5, pady=3)
    num_runs_entry = tk.Entry(ga_frame)
    num_runs_entry.insert(0, "10")
    num_runs_entry.grid(row=4, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(ga_frame, text="Kiểu lai:").grid(row=5, column=0, sticky="w", padx=5, pady=3)
    crossover_options = {"Lai một điểm": "one_point", "Lai ngẫu nhiên": "uniform"}
    crossover_combo = ttk.Combobox(ga_frame, values=list(crossover_options.keys()), state="readonly")
    crossover_combo.current(0)
    crossover_combo.grid(row=5, column=1, sticky="ew", padx=5, pady=3)

    run_button = tk.Button(ga_frame, text="Chạy thuật toán", command=run_ga)
    run_button.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")

    root.mainloop()
