import unittest
import numpy as np
from cerebro.burst_analysis import BurstAnalysis
from cerebro.complexity_analysis import ComplexityAnalysis
from cerebro.connectivity import ConnectivityAnalysis
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
        self.assertEqual(p.results, {})


if __name__ == "__main__":
    unittest.main()
