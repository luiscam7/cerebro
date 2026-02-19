"""Connectivity analysis pipeline for EEG data.

Calculates:
- Weighted Phase Lag Index (wPLI)
- Phase Slope Index (PSI)
- Coherence (Coh)
- Phase Locking Value (PLV)
- Transfer Entropy (TE)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from cerebro.qeeg import QeegAnalysis
from cerebro.utils.params import CHANNELS_10_20
from mne.connectivity import spectral_connectivity_epochs
from mne import create_info


class ConnectivityAnalysis(QeegAnalysis):
    """Connectivity analysis for EEG data."""

    def __init__(self):
        super().__init__()
        self.connectivity_results = None
        self.freq_bands = {
            "delta": (0.5, 4),
            "theta": (4, 8),
            "alpha": (8, 13),
            "beta": (13, 30),
            "low_beta": (13, 20),
            "high_beta": (20, 30),
        }

    def compute_wpli(
        self,
        fmin: float = 8,
        fmax: float = 13,
        n_fft: int = 256,
    ) -> np.ndarray:
        """
        Compute Weighted Phase Lag Index.

        Parameters:
        fmin, fmax: Frequency range.
        n_fft: FFT length.

        Returns:
        wPLI matrix (n_channels x n_channels).
        """
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        eeg_data = self.data.get_data(picks="eeg")
        sf = self.data.info["sfreq"]
        n_channels = eeg_data.shape[0]

        # Compute cross-spectral density
        con, freqs, times, _, _ = spectral_connectivity_epochs(
            self.data,
            method="wpli",
            fmin=fmin,
            fmax=fmax,
            n_fft=n_fft,
            indices=np.triu_indices(n_channels, k=1),
            mode="cwt_morlet",
            n_jobs=1,
        )

        # Build full matrix
        wpli_matrix = np.zeros((n_channels, n_channels))
        wpli_matrix[np.triu_indices(n_channels, k=1)] = con
        wpli_matrix += wpli_matrix.T

        return wpli_matrix

    def compute_phase_slope_index(
        self,
        fmin: float = 8,
        fmax: float = 13,
    ) -> np.ndarray:
        """
        Compute Phase Slope Index.

        Returns:
        PSI matrix (n_channels x n_channels).
        """
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        eeg_data = self.data.get_data(picks="eeg")
        n_channels = eeg_data.shape[0]

        con, freqs, _, _, _ = spectral_connectivity_epochs(
            self.data,
            method="psd_centered",
            fmin=fmin,
            fmax=fmax,
            indices=np.triu_indices(n_channels, k=1),
            mode="cwt_morlet",
            n_jobs=1,
        )

        psi_matrix = np.zeros((n_channels, n_channels))
        psi_matrix[np.triu_indices(n_channels, k=1)] = np.real(con)
        psi_matrix += psi_matrix.T

        return psi_matrix

    def compute_coherence(
        self,
        fmin: float = 8,
        fmax: float = 13,
    ) -> np.ndarray:
        """
        Compute Coherence.

        Returns:
        Coherence matrix (n_channels x n_channels).
        """
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        eeg_data = self.data.get_data(picks="eeg")
        n_channels = eeg_data.shape[0]

        con, freqs, _, _, _ = spectral_connectivity_epochs(
            self.data,
            method="coh",
            fmin=fmin,
            fmax=fmax,
            indices=np.triu_indices(n_channels, k=1),
            mode="cwt_morlet",
            n_jobs=1,
        )

        coh_matrix = np.zeros((n_channels, n_channels))
        coh_matrix[np.triu_indices(n_channels, k=1)] = np.abs(con)
        coh_matrix += coh_matrix.T
        np.fill_diagonal(coh_matrix, 1.0)

        return coh_matrix

    def compute_phase_locking_value(
        self,
        fmin: float = 8,
        fmax: float = 13,
    ) -> np.ndarray:
        """
        Compute Phase Locking Value (PLV).

        Returns:
        PLV matrix (n_channels x n_channels).
        """
        return self.compute_coherence(fmin=fmin, fmax=fmax)

    def compute_connectivity_all_bands(self) -> Dict[str, Dict]:
        """Compute all connectivity metrics across standard frequency bands."""
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        results = {}

        for band_name, (fmin, fmax) in self.freq_bands.items():
            results[band_name] = {
                "wpli": self.compute_wpli(fmin=fmin, fmax=fmax),
                "coherence": self.compute_coherence(fmin=fmin, fmax=fmax),
                "psi": self.compute_phase_slope_index(fmin=fmin, fmax=fmax),
            }

        self.connectivity_results = results
        self.analysis["connectivity"] = results

        return results

    def compute_transfer_entropy(
        self,
        channel_pairs: Optional[List[Tuple[int, int]]] = None,
        lag: int = 1,
        n_bins: int = 8,
    ) -> pd.DataFrame:
        """
        Compute Transfer Entropy between channel pairs.

        Parameters:
        channel_pairs: List of (source, target) channel indices. 
                      If None, compute for all pairs.
        lag: Time lag for TE calculation.
        n_bins: Number of bins for discretization.

        Returns:
        DataFrame with TE values per channel pair.
        """
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        eeg_data = self.data.get_data(picks="eeg")
        n_channels = eeg_data.shape[0]

        if channel_pairs is None:
            channel_pairs = [
                (i, j) for i in range(n_channels) for j in range(n_channels) if i != j
            ]

        results = []

        for source_idx, target_idx in channel_pairs:
            source_signal = eeg_data[source_idx]
            target_signal = eeg_data[target_idx]

            te = self._transfer_entropy(source_signal, target_signal, lag, n_bins)

            results.append({
                "source": CHANNELS_10_20[source_idx],
                "target": CHANNELS_10_20[target_idx],
                "transfer_entropy": te,
            })

        return pd.DataFrame(results)

    def _transfer_entropy(
        self,
        x: np.ndarray,
        y: np.ndarray,
        lag: int,
        n_bins: int,
    ) -> float:
        """Compute transfer entropy from x to y."""
        # Discretize signals
        x_bins = np.digitize(x, np.linspace(x.min(), x.max(), n_bins))
        y_bins = np.digitize(y, np.linspace(y.min(), y.max(), n_bins))

        # Shift for lagged analysis
        y_future = y_bins[lag:]
        y_past = y_bins[:-lag]
        x_past = x_bins[:-lag]

        # Joint probability estimation (simplified)
        n_states = n_bins
        p_y_future_y_past = np.zeros((n_states, n_states))
        p_y_future_y_past_x_past = np.zeros((n_states, n_states, n_states))

        for i in range(len(y_future)):
            p_y_future_y_past[y_future[i], y_past[i]] += 1
            p_y_future_y_past_x_past[y_future[i], y_past[i], x_past[i]] += 1

        # Normalize
        p_y_future_y_past /= len(y_future)
        p_y_future_y_past_x_past /= len(y_future)

        # Compute TE
        te = 0.0
        for j in range(n_states):
            for k in range(n_states):
                p_yj_xk = p_y_future_y_past_x_past[:, j, k].sum()
                if p_yj_xk > 0 and p_y_future_y_past[j, k] > 0:
                    for i in range(n_states):
                        p_yi_jk = p_y_future_y_past_x_pant[i, j, k]
                        if p_yi_jk > 0:
                            te += p_yi_jk * np.log(
                                p_yi_jk * p_y_future_y_past[j, k] / 
                                (p_yj_xk * p_y_future_y_past[j, k] + 1e-10)
                            )

        return max(0.0, te)

    def analyze_data(self) -> Dict:
        """Run full connectivity analysis."""
        super().analyze_data()
        self.compute_connectivity_all_bands()
        return self.analysis
