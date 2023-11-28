import json
from tkinter import filedialog
from cerebrus.qeeg import QeegAnalysis

def select_file_and_process():

    file_path = filedialog.askopenfilename(
        title="Select EEG Data File",
    )

    if not file_path:
        print("No file selected.")
        return

    cerebro = QeegAnalysis()
    cerebro.load_data(file_path, source='tdbrain')
    cerebro.preprocess_data()

    print("Data loaded and processed.")
    cerebro.analyze_data()

    cerebro.write_hdf5("notebooks/test.hdf5")


if __name__ == "__main__":
    processed_data = select_file_and_process()
