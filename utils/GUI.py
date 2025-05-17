import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from problem.genetic import GeneticAlgorithm
from problem.knapsack import KnapsackProblem

def start():
# Khởi tạo danh sách sản phẩm
    products = []

    # Thêm sản phẩm
    def add_product():
        name = name_entry.get()
        try:
            weight = float(weight_entry.get())
            value = float(value_entry.get())
            max_qty = int(max_qty_entry.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ cho trọng lượng, giá trị và số lượng.")
            return
        products.append({"name": name, "weight": weight, "value": value, "Max_quantity": max_qty})
        update_table()
        name_entry.delete(0, tk.END)
        weight_entry.delete(0, tk.END)
        value_entry.delete(0, tk.END)
        max_qty_entry.delete(0, tk.END)

    # Cập nhật bảng
    def update_table():
        for row in tree.get_children():
            tree.delete(row)
        for i, p in enumerate(products):
            tree.insert("", "end", iid=i, values=(p["name"], p["weight"], p["value"], p["Max_quantity"]))

    # Xoá sản phẩm
    def delete_product():
        selected = tree.selection()
        if selected:
            for idx in reversed(selected):
                del products[int(idx)]
            update_table()
        else:
            messagebox.showwarning("Chọn dòng", "Vui lòng chọn sản phẩm để xoá.")

    # Nhập Excel
    def import_excel():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            try:
                df = pd.read_excel(file_path)
                for _, row in df.iterrows():
                    products.append({
                        "name": row["name"],
                        "weight": float(row["weight"]),
                        "value": float(row["value"]),
                        "Max_quantity": int(row["Max_quantity"])
                    })
                update_table()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc file Excel: {e}")

    #chạy thuật toán 
    def run_ga():
        if not products:
            messagebox.showerror("Lỗi", "Chưa có sản phẩm để tính toán.")
            return

        try:
            capacity = float(capacity_entry.get())
            generations = int(generations_entry.get())
            population_size = int(pop_size_entry.get())
            mutation_rate = float(mutation_rate_entry.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập thông số hợp lệ.")
            return

        problem = KnapsackProblem(products, capacity= capacity)

        sovler = GeneticAlgorithm(problem= problem, populationSize= population_size, generations=generations, crossoverType= 'uniform' ,mutationRate=mutation_rate)
        logs = sovler.run() 
        plot_chart(logs)

    # Vẽ biểu đồ
    def plot_chart(logs):
        generations = [log["generation"] for log in logs]
        best_fitness = [log["best"] for log in logs]
        avg_fitness = [log["avg"] for log in logs]
        worst_fitness = [log["worst"] for log in logs]

        plt.figure(figsize=(10, 6))
        plt.plot(generations, best_fitness, label="Best Fitness", color='green')
        plt.plot(generations, avg_fitness, label="Average Fitness", color='blue')
        plt.plot(generations, worst_fitness, label="Worst Fitness", color='red')

        plt.title("Tiến hoá qua các thế hệ")
        plt.xlabel("Thế hệ")
        plt.ylabel("Giá trị Fitness")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # GUI chính
    root = tk.Tk()
    root.title("Bài toán Cái túi - Genetic Algorithm")

    # Cấu hình co giãn tổng thể (không chiếm hết không gian)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=0)  # Không giãn theo chiều dọc

    # FORM NHẬP SẢN PHẨM (co giãn vừa phải)
    form_frame = tk.Frame(root, padx=10, pady=10)
    form_frame.pack(fill="x", expand=False)

    # Cấu hình lưới cho form
    form_frame.columnconfigure(1, weight=1)  # Chỉ cột Entry giãn nhẹ

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

    # BẢNG SẢN PHẨM (giãn có giới hạn)
    tree_frame = tk.Frame(root)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

    tree = ttk.Treeview(tree_frame, columns=("name", "weight", "value", "max_quantity"), 
                    show="headings", height=8)  # Giới hạn chiều cao
    for col in ("name", "weight", "value", "max_quantity"):
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=100, anchor="center")

    tree.pack(side="left", fill="both", expand=True)

    # Thanh cuộn
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # NÚT ĐIỀU KHIỂN (không giãn)
    control_frame = tk.Frame(root)
    control_frame.pack(pady=(0,10))

    delete_button = tk.Button(control_frame, text="Xoá sản phẩm", command=delete_product)
    delete_button.pack(side="left", padx=5)

    import_button = tk.Button(control_frame, text="Import Excel", command=import_excel)
    import_button.pack(side="left", padx=5)

    # CẤU HÌNH GA (giãn nhẹ)
    ga_frame = tk.LabelFrame(root, text="Cấu hình thuật toán di truyền", padx=10, pady=10)
    ga_frame.pack(fill="x", padx=10, pady=(0,10))

    ga_frame.columnconfigure(1, weight=1)  # Chỉ giãn cột nhập liệu

    tk.Label(ga_frame, text="Sức chứa túi:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
    capacity_entry = tk.Entry(ga_frame)
    capacity_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(ga_frame, text="Số thế hệ:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
    generations_entry = tk.Entry(ga_frame)
    generations_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(ga_frame, text="Số cá thể trong quần thể:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
    pop_size_entry = tk.Entry(ga_frame)
    pop_size_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=3)

    tk.Label(ga_frame, text="Tỷ lệ đột biến:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
    mutation_rate_entry = tk.Entry(ga_frame)
    mutation_rate_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=3)

    run_button = tk.Button(ga_frame, text="Chạy thuật toán", command=run_ga)
    run_button.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

    root.mainloop()
