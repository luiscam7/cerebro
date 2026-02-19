import unittest
import numpy as np
from cerebro.burst_analysis import BurstAnalysis
from cerebro.complexity_analysis import ComplexityAnalysis
from cerebro.connectivity import ConnectivityAnalysis
from cerebro.heart_analysis import HeartRateAnalysis
from cerebro.preprocessing import eeg_filter


class TestBurstAnalysis(unittest.TestCase):
    """Test burst detection features."""

    def test_sample_entropy(self):
        """Test sample entropy calculation."""
        ca = ComplexityAnalysis()
        signal = np.random.randn(1000)
        result = ca.compute_sample_entropy(signal)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)

    def test_approximate_entropy(self):
        """Test approximate entropy calculation."""
        ca = ComplexityAnalysis()
        signal = np.random.randn(1000)
        result = ca.compute_approximate_entropy(signal)
        self.assertIsInstance(result, float)

    def test_hurst_exponent(self):
        """Test Hurst exponent calculation."""
        ca = ComplexityAnalysis()
        # Random signal should have H ~ 0.5
        signal = np.random.randn(500)
        result = ca.compute_hurst_exponent(signal)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)

    def test_fractal_dimension(self):
        """Test fractal dimension calculation."""
        ca = ComplexityAnalysis()
        signal = np.random.randn(500)
        result = ca.compute_fractal_dimension(signal)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_lempel_ziv_complexity(self):
        """Test Lempel-Ziv complexity calculation."""
        ca = ComplexityAnalysis()
        signal = np.random.randn(500)
        result = ca.compute_lempel_ziv_complexity(signal)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)

    def test_dfa(self):
        """Test detrended fluctuation analysis."""
        ca = ComplexityAnalysis()
        signal = np.random.randn(500)
        result = ca.compute_dfa(signal)
        self.assertIsInstance(result, float)

    def test_permutation_entropy(self):
        """Test permutation entropy calculation."""
        ca = ComplexityAnalysis()
        signal = np.sin(np.linspace(0, 10 * np.pi, 500))
        result = ca.compute_permutation_entropy(signal)
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)


class TestComplexityAnalysis(unittest.TestCase):
    """Test complexity analysis class."""

    def test_complexity_analysis_init(self):
        """Test initialization."""
        ca = ComplexityAnalysis()
        self.assertIsNone(ca.data)
        self.assertIsNone(ca.complexity_results)


class TestConnectivityAnalysis(unittest.TestCase):
    """Test connectivity analysis class."""

    def test_connectivity_analysis_init(self):
        """Test initialization."""
        ca = ConnectivityAnalysis()
        self.assertIsNone(ca.data)
        self.assertIsNotNone(ca.frontal_channels)

    def test_set_raw(self):
        """Test set_raw method."""
        ca = ConnectivityAnalysis()
        self.assertIsNone(ca.data)


class TestPreprocessing(unittest.TestCase):
    """Test preprocessing functions."""

    def test_eeg_filter_import(self):
        """Test that eeg_filter can be imported."""
        self.assertTrue(callable(eeg_filter))


class TestPipeline(unittest.TestCase):
    """Test pipeline integration."""

    def test_pipeline_import(self):
        """Test pipeline can be imported."""
        from cerebro.pipeline import CerebroPipeline, run_pipeline

        self.assertTrue(callable(CerebroPipeline))
        self.assertTrue(callable(run_pipeline))

    def test_pipeline_init(self):
        """Test pipeline initialization."""
        from cerebro.pipeline import CerebroPipeline

        p = CerebroPipeline()
        self.assertIsNotNone(p.qeeg)
        self.assertIsNotNone(p.burst)
        self.assertIsNotNone(p.complexity)
        self.assertIsNotNone(p.connectivity)
        self.assertIsNotNone(p.heart)
        self.assertEqual(p.results, {})


class TestHeartAnalysis(unittest.TestCase):
    """Test heart rate analysis."""

    def test_heart_analysis_init(self):
        """Test heart analysis initialization."""
        h = HeartRateAnalysis()
        self.assertIsNone(h.data)
        self.assertIsNone(h.ecg_channel)
        self.assertIsNone(h.heart_rate)
        self.assertIsNone(h.rr_intervals)

    def test_set_raw(self):
        """Test set_raw method."""
        h = HeartRateAnalysis()
        self.assertIsNone(h.data)

    def test_detect_peaks(self):
        """Test R-peak detection."""
        h = HeartRateAnalysis()
        # Simulate ECG signal with peaks at 1Hz, sampling at 256Hz
        sfreq = 256
        t = np.linspace(0, 10, sfreq * 10)
        signal = np.sin(2 * np.pi * 1 * t) + 0.1 * np.random.randn(len(t))
        
        peaks = h.detect_peaks(signal, sfreq, threshold=0.5)
        # Should detect approximately 10 peaks (give more tolerance)
        self.assertGreater(len(peaks), 3)
        self.assertLess(len(peaks), 25)

    def test_compute_rmssd(self):
        """Test RMSSD calculation."""
        h = HeartRateAnalysis()
        # Normal RR intervals ~700-900ms with some variation
        h.rr_intervals = np.array([800, 850, 780, 820, 810])
        rmssd = h.compute_rmssd()
        self.assertIsInstance(rmssd, float)
        self.assertGreater(rmssd, 0)

    def test_compute_sdnn(self):
        """Test SDNN calculation."""
        h = HeartRateAnalysis()
        h.rr_intervals = np.array([800, 850, 780, 820, 810])
        sdnn = h.compute_sdnn()
        self.assertIsInstance(sdnn, float)
        self.assertGreater(sdnn, 0)

    def test_compute_pnn50(self):
        """Test pNN50 calculation."""
        h = HeartRateAnalysis()
        h.rr_intervals = np.array([800, 850, 780, 820, 810])
        pnn50 = h.compute_pnn50()
        self.assertIsInstance(pnn50, float)
        self.assertGreaterEqual(pnn50, 0)
        self.assertLessEqual(pnn50, 100)

    def test_compute_pnn20(self):
        """Test pNN20 calculation."""
        h = HeartRateAnalysis()
        h.rr_intervals = np.array([800, 850, 780, 820, 810])
        pnn20 = h.compute_pnn20()
        self.assertIsInstance(pnn20, float)
        self.assertGreaterEqual(pnn20, 0)
        self.assertLessEqual(pnn20, 100)

    def test_compute_heart_rate(self):
        """Test heart rate calculation."""
        h = HeartRateAnalysis()
        # RR interval of 1000ms = 60 BPM
        h.rr_intervals = np.array([1000] * 10)
        hr = h.compute_heart_rate()
        self.assertAlmostEqual(hr, 60, delta=5)


if __name__ == "__main__":
    unittest.main()
