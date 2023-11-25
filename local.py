import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import filedialog
from cerebrus.cerebro import Cerebro  

def select_file_and_process():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(
        title="Select EEG Data File",
        filetypes=[("All files", "*.*")]
    )

    if not file_path:
        print("No file selected.")
        return

    cerebro = Cerebro()
    cerebro.load_data(file_path, source='tdbrain')
    processed_data = cerebro.preprocess_data()

    print("Data loaded and processed.")
    processed_data.compute_psd(fmin=2.2, fmax=25).plot()
    plt.show()


if __name__ == "__main__":
    processed_data = select_file_and_process()
