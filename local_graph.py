import matplotlib.pyplot as plt
from tkinter import filedialog
from cerebrus import Cerebro

def select_file_and_process():

    file_path = filedialog.askopenfilename(
        title="Select EEG Data File",
    )

    if not file_path:
        print("No file selected.")
        return

    cerebro = Cerebro()
    cerebro.load_data(file_path, source='tdbrain')
    cerebro.preprocess_data()

    print("Data loaded and processed.")
    assert cerebro.raw_data != cerebro.filt_data
    cerebro.raw_data.compute_psd().plot()
    cerebro.filt_data.compute_psd().plot()

    plt.show()



if __name__ == "__main__":
    processed_data = select_file_and_process()
