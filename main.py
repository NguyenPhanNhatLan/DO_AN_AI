
# if __name__ == "__main__":
#     start()

# from tkinter import Tk
# from utils.GUI import KnapsackUI

# if __name__ == "__main__":
#     root = Tk()
#     app = KnapsackUI(root)
#     root.mainloop()

from tkinter import Tk
from utils.AVG import GAApp  # giả sử code GUI vừa rồi bạn lưu ở đây

if __name__ == "__main__":
    root = Tk()
    app = GAApp(root)
    root.mainloop()