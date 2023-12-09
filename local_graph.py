import matplotlib.pyplot as plt
from tkinter import filedialog
from cerebro import Cerebro

def select_file_and_process():

    file_path = filedialog.askopenfilename(
        title="Select EEG Data File",
    )

    if not file_path:
        print("No file selected.")
        return

    cerebro = Cerebro()
    cerebro.load_data(file_path, source='tuh')
    cerebro.preprocess_data()

    bands = {'Delta (0-4 Hz)': (0, 4), 'Theta (4-8 Hz)': (4, 8),
         'Alpha (8-12 Hz)': (8, 12), 'Beta (12-30 Hz)': (12, 30),
         'Gamma (30-45 Hz)': (30, 45)}

    print("Data loaded and processed.")
    cerebro.filt_data.compute_psd().plot_topomap(bands = bands, cmap='plasma', normalize=True)
    cerebro.filt_data.compute_psd(fmin=2, fmax=25).plot_topo(dB=False)
    cerebro.filt_data.compute_psd().plot()
    cerebro.filt_data.plot()
    plt.show()


if __name__ == "__main__":
    processed_data = select_file_and_process()
