import json
import time

from cerebro.connectivity import ConnectivityAnalysis


def select_file_and_process():
    file_path = input("Enter filepath: ")

    start = time.time()
    cerebro = ConnectivityAnalysis()
    cerebro.load_data(file_path, source="tuh")
    cerebro.preprocess_data()

    print("Data loaded and processed.")
    cerebro.analyze_data()
    print("EEG processing took", time.time() - start, "seconds.")
    cerebro.write_json("notebooks/test.json")


if __name__ == "__main__":
    processed_data = select_file_and_process()
