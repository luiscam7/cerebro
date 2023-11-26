import json
from tkinter import filedialog
from cerebrus.qeeg import PowerSpectralAnalysis  

def select_file_and_process():

    file_path = filedialog.askopenfilename(
        title="Select EEG Data File",
    )

    if not file_path:
        print("No file selected.")
        return

    cerebro = PowerSpectralAnalysis()
    cerebro.load_data(file_path, source='tdbrain')
    cerebro.preprocess_data()

    print("Data loaded and processed.")
    analysis_json = cerebro.analyze_data()

    with open("test.json", "w") as f:
        json.dump(analysis_json, f)


if __name__ == "__main__":
    processed_data = select_file_and_process()
