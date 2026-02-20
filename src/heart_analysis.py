"""Heart rate and HRV analysis from ECG/EOG data.

Metrics:
- Heart Rate (BPM)
- HRV: RMSSD, SDNN, pNN50, pNN20
- Frequency domain: LF, HF, LF/HF ratio
- Heart rate variability features
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from .qeeg import QeegAnalysis
from .utils.params import CHANNELS_10_20


class HeartRateAnalysis(QeegAnalysis):
    """Heart rate and HRV analysis from ECG channels."""

    def __init__(self):
        super().__init__()
        self.ecg_channel = None
        self.heart_rate = None
        self.rr_intervals = None
        self.hrv_results = None
        self.data = None

    def set_raw(self, raw):
        """Set raw EEG data directly."""
        self.data = raw

    def find_ecg_channel(self) -> Optional[str]:
        """Find ECG channel in data."""
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        ch_names = self.data.ch_names

        # Look for ECG channel
        for ch in ch_names:
            if "ecg" in ch.lower() or "ekg" in ch.lower():
                self.ecg_channel = ch
                return ch

        # Check for EOG as fallback
        for ch in ch_names:
            if "eog" in ch.lower():
                self.ecg_channel = ch
                return ch

        return None

    def detect_peaks(
        self,
        signal: np.ndarray,
        sfreq: float,
        threshold: float = 0.5,
        min_distance: float = 0.3,
    ) -> np.ndarray:
        """
        Detect R-peaks in ECG signal using threshold-based peak detection.

        Parameters:
            signal: ECG signal.
            sfreq: Sampling frequency.
            threshold: Detection threshold (0-1 relative to max).
            min_distance: Minimum distance between peaks (seconds).

        Returns:
            Array of peak indices.
        """
        # Bandpass filter to isolate QRS
        from mne.filter import filter_data

        filtered = filter_data(signal.astype(float), sfreq, 5, 45, method="iir")

        # Normalize
        filtered = filtered - np.mean(filtered)
        filtered = filtered / (np.std(filtered) + 1e-10)

        # Threshold detection
        threshold_val = threshold * np.max(filtered)
        peaks = np.where(filtered > threshold_val)[0]

        # Minimum distance filter
        min_samples = int(min_distance * sfreq)
        if len(peaks) > 1:
            filtered_peaks = [peaks[0]]
            for p in peaks[1:]:
                if p - filtered_peaks[-1] >= min_samples:
                    filtered_peaks.append(p)
            peaks = np.array(filtered_peaks)

        return peaks

    def compute_rr_intervals(
        self,
        channel: Optional[str] = None,
        threshold: float = 0.5,
    ) -> np.ndarray:
        """
        Compute RR intervals from ECG channel.

        Parameters:
            channel: ECG channel name. If None, auto-detect.
            threshold: Peak detection threshold.

        Returns:
            RR intervals in milliseconds.
        """
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        if channel is None:
            channel = self.find_ecg_channel()
            if channel is None:
                raise ValueError("No ECG channel found. Please specify channel name.")

        sfreq = self.data.info["sfreq"]
        signal = self.data.get_data(picks=[channel]).flatten()

        peaks = self.detect_peaks(signal, sfreq, threshold=threshold)

        # Compute RR intervals
        rr = np.diff(peaks) / sfreq * 1000  # Convert to ms

        self.rr_intervals = rr
        return rr

    def compute_heart_rate(self) -> float:
        """
        Compute average heart rate in BPM.

        Returns:
            Heart rate in beats per minute.
        """
        if self.rr_intervals is None:
            self.compute_rr_intervals()

        if len(self.rr_intervals) == 0:
            return 0.0

        # Remove outliers (生理上不合理的心跳间期)
        rr = self.rr_intervals.copy()
        rr = rr[(rr > 300) & (rr < 2000)]  # 30-200 BPM range

        if len(rr) == 0:
            return 0.0

        self.heart_rate = 60000 / np.mean(rr)
        return self.heart_rate

    def compute_rmssd(self) -> float:
        """
        Compute RMSSD (Root Mean Square of Successive Differences).

        Returns:
            RMSSD in milliseconds.
        """
        if self.rr_intervals is None:
            self.compute_rr_intervals()

        if len(self.rr_intervals) < 2:
            return 0.0

        successive_diffs = np.diff(self.rr_intervals)
        rmssd = np.sqrt(np.mean(successive_diffs**2))

        return rmssd

    def compute_sdnn(self) -> float:
        """
        Compute SDNN (Standard Deviation of NN intervals).

        Returns:
            SDNN in milliseconds.
        """
        if self.rr_intervals is None:
            self.compute_rr_intervals()

        if len(self.rr_intervals) < 2:
            return 0.0

        return np.std(self.rr_intervals)

    def compute_pnn50(self) -> float:
        """
        Compute pNN50 (Percentage of successive RR intervals differing by > 50ms).

        Returns:
            pNN50 percentage.
        """
        if self.rr_intervals is None:
            self.compute_rr_intervals()

        if len(self.rr_intervals) < 2:
            return 0.0

        successive_diffs = np.abs(np.diff(self.rr_intervals))
        nn50 = np.sum(successive_diffs > 50)

        return (nn50 / len(successive_diffs)) * 100

    def compute_pnn20(self) -> float:
        """
        Compute pNN20 (Percentage of successive RR intervals differing by > 20ms).

        Returns:
            pNN20 percentage.
        """
        if self.rr_intervals is None:
            self.compute_rr_intervals()

        if len(self.rr_intervals) < 2:
            return 0.0

        successive_diffs = np.abs(np.diff(self.rr_intervals))
        nn20 = np.sum(successive_diffs > 20)

        return (nn20 / len(successive_diffs)) * 100

    def compute_hrv_frequency(self) -> Dict[str, float]:
        """
        Compute frequency domain HRV features.

        Returns:
            Dictionary with LF, HF power and LF/HF ratio.
        """
        if self.rr_intervals is None:
            self.compute_rr_intervals()

        if len(self.rr_intervals) < 10:
            return {"lf": 0.0, "hf": 0.0, "lf_hf_ratio": 0.0}

        # Interpolate to evenly spaced time series
        from scipy.interpolate import interp1d

        fs = 4  # Resample to 4 Hz
        time = np.cumsum(self.rr_intervals) / 1000
        time = time - time[0]

        interp_func = interp1d(
            time, self.rr_intervals, kind="cubic", fill_value="extrapolate"
        )
        time_regular = np.arange(0, time[-1], 1 / fs)
        rr_regular = interp_func(time_regular)

        # Compute power spectral density
        from scipy.signal import welch

        freqs, psd = welch(rr_regular, fs=fs, nperseg=min(256, len(rr_regular)))

        # Define frequency bands
        lf_mask = (freqs >= 0.04) & (freqs < 0.15)
        hf_mask = (freqs >= 0.15) & (freqs < 0.4)

        lf_power = np.trapz(psd[lf_mask], freqs[lf_mask])
        hf_power = np.trapz(psd[hf_mask], freqs[hf_mask])

        lf_hf_ratio = lf_power / (hf_power + 1e-10)

        return {
            "lf": lf_power,
            "hf": hf_power,
            "lf_hf_ratio": lf_hf_ratio,
        }

    def compute_all_hrv(self, channel: Optional[str] = None) -> Dict:
        """
        Compute all HRV metrics.

        Parameters:
            channel: ECG channel name.

        Returns:
            Dictionary with all HRV metrics.
        """
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        # Find or use specified channel
        if channel is None:
            channel = self.find_ecg_channel()
            if channel is None:
                return {"error": "No ECG channel found"}

        # Compute RR intervals
        self.compute_rr_intervals(channel=channel)

        # Compute metrics
        hr = self.compute_heart_rate()
        rmssd = self.compute_rmssd()
        sdnn = self.compute_sdnn()
        pnn50 = self.compute_pnn50()
        pnn20 = self.compute_pnn20()
        freq = self.compute_hrv_frequency()

        self.hrv_results = {
            "channel": channel,
            "heart_rate_bpm": hr,
            "rmssd_ms": rmssd,
            "sdnn_ms": sdnn,
            "pnn50_percent": pnn50,
            "pnn20_percent": pnn20,
            "lf_power": freq["lf"],
            "hf_power": freq["hf"],
            "lf_hf_ratio": freq["lf_hf_ratio"],
            "n_rr_intervals": len(self.rr_intervals),
        }

        self.analysis["heart_rate"] = self.hrv_results

        return self.hrv_results

    def analyze_data(self) -> Dict:
        """Run heart rate analysis."""
        return self.compute_all_hrv()
