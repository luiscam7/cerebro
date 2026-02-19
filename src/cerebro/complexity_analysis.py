"""Complexity analysis pipeline for EEG data.

Calculates:
- Sample Entropy (SampEn)
- Approximate Entropy (ApEn)
- Hurst Exponent (H)
- Fractal Dimension (FD)
- Lempel-Ziv Complexity (LZC)
- Detrended Fluctuation Analysis (DFA)
- Permutation Entropy (PE)
"""

import numpy as np
import pandas as pd
from typing import Dict, List
from cerebro.qeeg import QeegAnalysis
from cerebro.utils.params import CHANNELS_10_20


class ComplexityAnalysis(QeegAnalysis):
    """Complexity analysis for EEG data."""

    def __init__(self):
        super().__init__()
        self.complexity_results = None
        self.data = None

    def set_raw(self, raw):
        """Set raw EEG data directly."""
        self.data = raw

    def compute_sample_entropy(
        self, signal: np.ndarray, m: int = 2, r: float = 0.2
    ) -> float:
        """
        Compute Sample Entropy.

        Parameters:
        signal: Time series data.
        m: Embedding dimension.
        r: Tolerance (usually 0.1-0.2 of std).

        Returns:
        Sample entropy value.
        """
        N = len(signal)
        r = r * np.std(signal)

        # Build template matrix
        def _maxdist(xi, xj):
            return max([abs(ua - va) for ua, va in zip(xi, xj)])

        def _phi(m):
            patterns = np.array([signal[i : i + m] for i in range(N - m)])
            count = np.zeros(N - m)
            for i in range(N - m):
                for j in range(N - m):
                    if i != j and _maxdist(patterns[i], patterns[j]) < r:
                        count[i] += 1
            return np.sum(count) / (N - m)

        phi_m = _phi(m)
        phi_m1 = _phi(m + 1)

        if phi_m == 0 or phi_m1 == 0:
            return 0.0

        return -np.log(phi_m1 / phi_m)

    def compute_approximate_entropy(
        self, signal: np.ndarray, m: int = 2, r: float = 0.2
    ) -> float:
        """
        Compute Approximate Entropy.

        Parameters:
        signal: Time series data.
        m: Embedding dimension.
        r: Tolerance.

        Returns:
        Approximate entropy value.
        """
        N = len(signal)
        r = r * np.std(signal)

        def _maxdist(xi, xj):
            return max([abs(ua - va) for ua, va in zip(xi, xj)])

        def _phi(m):
            patterns = np.array([signal[i : i + m] for i in range(N - m + 1)])
            C = np.zeros(N - m + 1)
            for i in range(N - m + 1):
                for j in range(N - m + 1):
                    if _maxdist(patterns[i], patterns[j]) < r:
                        C[i] += 1
            return np.sum(np.log(C)) / (N - m + 1)

        return _phi(m) - _phi(m + 1)

    def compute_hurst_exponent(self, signal: np.ndarray) -> float:
        """
        Compute Hurst Exponent using R/S analysis.

        Returns:
        Hurst exponent (H):
            H > 0.5: Long-term persistence (trending)
            H = 0.5: Random walk
            H < 0.5: Anti-persistent (mean-reverting)
        """
        N = len(signal)
        signal = np.array(signal)
        mean_val = np.mean(signal)
        y = np.cumsum(signal - mean_val)
        rs_values = []

        for n in range(10, N // 2):
            rs_n = []
            for start in range(0, N - n, n):
                segment = y[start : start + n]
                R = np.max(segment) - np.min(segment)
                S = np.std(signal[start : start + n])
                if S > 0:
                    rs_n.append(R / S)
            if rs_n:
                rs_values.append((n, np.mean(rs_n)))

        if not rs_values:
            return 0.5

        # Fit log-log
        log_n = np.log([x[0] for x in rs_values])
        log_rs = np.log([x[1] for x in rs_values])

        coeffs = np.polyfit(log_n, log_rs, 1)
        return coeffs[0]

    def compute_fractal_dimension(
        self, signal: np.ndarray, n_segments: int = 10
    ) -> float:
        """
        Compute Fractal Dimension using Higuchi's method.

        Returns:
        Fractal dimension (typically 1-2 for EEG).
        """
        signal = np.array(signal)
        N = len(signal)

        L = []
        x = np.arange(1, n_segments + 1)

        for k in x:
            Lk = []
            for m in range(k):
                indices = np.arange(m, N, k)
                if len(indices) > 1:
                    Lmk = (
                        np.sum(np.abs(np.diff(signal[indices])))
                        * (N - 1)
                        / (len(indices) * k)
                    )
                    Lk.append(Lmk)
            if Lk:
                L.append(np.mean(Lk))

        if not L or np.sum(L) == 0:
            return 1.0

        log_k = np.log(x)
        log_L = np.log(np.array(L))

        coeffs = np.polyfit(log_k, log_L, 1)
        return -coeffs[0]

    def compute_lempel_ziv_complexity(
        self, signal: np.ndarray, threshold: float = 0.5
    ) -> float:
        """
        Compute Lempel-Ziv Complexity.

        Parameters:
        signal: Time series data.
        threshold: Threshold for binarization (relative to median).

        Returns:
        LZC value (higher = more complex).
        """
        # Binarize signal
        median = np.median(signal)
        binary = "".join(["1" if s > median * threshold else "0" for s in signal])

        c = 1
        j = 0
        i = 1

        while i < len(binary):
            if binary[i] != binary[j]:
                i += 1
            else:
                found = False
                for k in range(1, i + 1):
                    if i + k > len(binary):
                        break
                    if binary[i : i + k] == binary[j : j + k]:
                        found = True
                        break
                if not found:
                    c += 1
                    j = i
                i += 1

        return c

    def compute_dfa(self, signal: np.ndarray) -> float:
        """
        Compute Detrended Fluctuation Analysis alpha.

        Returns:
        DFA alpha:
            alpha < 0.5: Anti-persistent
            alpha = 0.5: Uncorrelated
            alpha > 0.5: Persistent
        """
        signal = np.array(signal)
        N = len(signal)

        # Cumulative sum
        y = np.cumsum(signal - np.mean(signal))

        # Different window sizes
        box_sizes = np.unique(np.logspace(0, np.log10(N // 4), dtype=int))
        F = []

        for s in box_sizes:
            n_boxes = N // s
            Fs = []
            for i in range(n_boxes):
                start = i * s
                end = start + s
                if end > N:
                    break
                segment = y[start:end]
                coeffs = np.polyfit(np.arange(s), segment, 1)
                fit = np.polyval(coeffs, np.arange(s))
                Fs.append(np.mean((segment - fit) ** 2))
            if Fs:
                F.append(np.mean(Fs))

        if not F:
            return 0.5

        log_s = np.log(box_sizes[: len(F)])
        log_F = np.log(np.array(F))

        coeffs = np.polyfit(log_s, log_F, 1)
        return coeffs[0] / 2

    def compute_permutation_entropy(
        self, signal: np.ndarray, m: int = 3, delay: int = 1
    ) -> float:
        """
        Compute Permutation Entropy.

        Parameters:
        signal: Time series data.
        m: Embedding dimension.
        delay: Time delay.

        Returns:
        Normalized permutation entropy (0-1).
        """
        N = len(signal)

        # Build permutation patterns
        patterns = []
        for i in range(0, N - delay * m, delay):
            pattern = np.argsort(signal[i : i + delay * m : delay])
            patterns.append(tuple(pattern))

        # Count patterns
        unique, counts = np.unique(patterns, axis=0, return_counts=True)
        probs = counts / len(patterns)

        # Shannon entropy
        entropy = -np.sum(probs * np.log(probs + 1e-10))

        # Normalize
        max_entropy = np.log(np.math.factorial(m))
        return entropy / max_entropy

    def compute_complexity_all_channels(self) -> pd.DataFrame:
        """Compute all complexity features across all 19 channels."""
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        eeg_data = self.data.get_data(picks="eeg")
        results = []

        for idx, channel in enumerate(CHANNELS_10_20):
            signal = eeg_data[idx]

            results.append(
                {
                    "channel": channel,
                    "sample_entropy": self.compute_sample_entropy(signal),
                    "approximate_entropy": self.compute_approximate_entropy(signal),
                    "hurst_exponent": self.compute_hurst_exponent(signal),
                    "fractal_dimension": self.compute_fractal_dimension(signal),
                    "lempel_ziv_complexity": self.compute_lempel_ziv_complexity(signal),
                    "dfa_alpha": self.compute_dfa(signal),
                    "permutation_entropy": self.compute_permutation_entropy(signal),
                }
            )

        self.complexity_results = pd.DataFrame(results)
        self.analysis["complexity"] = self.complexity_results.to_dict(orient="records")

        return self.complexity_results

    def analyze_data(self) -> Dict:
        """Run full complexity analysis."""
        super().analyze_data()
        self.compute_complexity_all_channels()
        return self.analysis
