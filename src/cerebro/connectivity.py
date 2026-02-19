import numpy as np
import networkx as nx
import scipy.signal
from cerebro.spectral_analysis import SpectralAnalysis
from cerebro.utils.params import ALPHA_BAND, STABLE_FRONTAL_SENSORS
from typing import Dict


class ConnectivityAnalysis(SpectralAnalysis):
    def __init__(self):
        super().__init__()
        self.frontal_channels = STABLE_FRONTAL_SENSORS
        self.data = None

    def set_raw(self, raw):
        """Set raw EEG data directly."""
        self.data = raw

    def calculate_all_coherence(self):
        data, times = self.data[:]
        sfreq = self.data.info["sfreq"]
        fmin, fmax = ALPHA_BAND
        n_channels = data.shape[0]
        channel_names = self.data.ch_names

        coherence_dict = {}

        # Calculate coherence for each unique pair of channels
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                f, Cxy = scipy.signal.coherence(
                    data[i], data[j], fs=sfreq, nperseg=1024, noverlap=512
                )
                idx_band = np.logical_and(f >= fmin, f <= fmax)
                coherence_value = np.mean(Cxy[idx_band])
                key = f"{channel_names[i]}-{channel_names[j]}"
                coherence_dict[key] = coherence_value

        return coherence_dict

    def calculate_median_frontal_coherence(self):
        frontal_data = self.data.copy().pick(self.frontal_channels)

        # Extract data and times
        data, times = frontal_data[:]
        sfreq = frontal_data.info["sfreq"]
        fmin, fmax = ALPHA_BAND
        n_channels = data.shape[0]
        coherence_values = []

        # Calculate coherence for each pair of frontal channels
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                f, Cxy = scipy.signal.coherence(
                    data[i], data[j], fs=sfreq, nperseg=1024, noverlap=512
                )
                idx_band = np.logical_and(f >= fmin, f <= fmax)
                coherence_value = np.mean(Cxy[idx_band])
                coherence_values.append(coherence_value)

        # Calculate and return the median coherence
        return np.median(coherence_values)

    def build_and_analyze_graph(self):
        coherence_data = self.calculate_all_coherence()
        G = nx.Graph()

        # Add nodes and edges to the graph
        for pair, coherence in coherence_data.items():
            node1, node2 = pair.split("-")
            G.add_edge(node1, node2, weight=coherence)

        # Remove edges below the 75% coherence threshold
        threshold = np.percentile(list(coherence_data.values()), 75)
        edges_to_remove = [
            (u, v) for u, v, w in G.edges(data=True) if w["weight"] < threshold
        ]
        G.remove_edges_from(edges_to_remove)

        # Calculate graph measures
        measures = {
            "degree": dict(G.degree(weight="weight")),
            "betweenness_centrality": nx.betweenness_centrality(G, weight="weight"),
            "closeness_centrality": nx.closeness_centrality(G, distance="weight")
            # Add other measures as needed
        }

        return measures

    def analyze_data(self) -> Dict:
        super().analyze_data()
        self.analysis["coherence"] = self.calculate_all_coherence()
        self.analysis[
            "median_frontal_coherence"
        ] = self.calculate_median_frontal_coherence()
        self.analysis["graph_measures"] = self.build_and_analyze_graph()
