"""Consolidated EEG analysis pipeline.

Runs all analyses in one go:
- Power spectral analysis (qEEG)
- Burst detection (alpha)
- Complexity features
- Connectivity (wPLI, coherence)
"""

import json
from typing import Dict, Optional
from pathlib import Path

from cerebro.qeeg import QeegAnalysis
from cerebro.burst_analysis import BurstAnalysis
from cerebro.complexity_analysis import ComplexityAnalysis
from cerebro.connectivity import ConnectivityAnalysis
from cerebro.io.writer import dict_to_json


class CerebroPipeline:
    """
    Consolidated pipeline that runs all EEG analyses.
    
    Usage:
        pipeline = CerebroPipeline()
        pipeline.load_data("path/to/eegfile.set")
        pipeline.preprocess_data()
        results = pipeline.run_full_analysis()
        pipeline.save_results("output.json")
    """

    def __init__(self):
        self.qeeg = QeegAnalysis()
        self.burst = BurstAnalysis()
        self.complexity = ComplexityAnalysis()
        self.connectivity = ConnectivityAnalysis()
        self.results = {}

    def load_data(self, file_path: str) -> None:
        """Load EEG data using any supported format."""
        self.qeeg.load_data(file_path)
        self.burst.set_raw(self.qeeg.data)
        self.complexity.set_raw(self.qeeg.data)
        self.connectivity.set_raw(self.qeeg.data)

    def preprocess_data(
        self,
        l_freq: float = 1.0,
        h_freq: float = 25.0,
        remove_powerline: bool = True,
    ) -> None:
        """Preprocess EEG data."""
        self.qeeg.preprocess_data(
            l_freq=l_freq,
            h_freq=h_freq,
            remove_powerline=remove_powerline,
        )
        # Share preprocessed data
        if self.qeeg.data is not None:
            self.burst.data = self.qeeg.data
            self.complexity.data = self.qeeg.data
            self.connectivity.data = self.qeeg.data

    def run_full_analysis(
        self,
        run_qeeg: bool = True,
        run_bursts: bool = True,
        run_complexity: bool = True,
        run_connectivity: bool = True,
    ) -> Dict:
        """
        Run all selected analyses.
        
        Parameters:
            run_qeeg: Compute power spectral metrics.
            run_bursts: Detect alpha bursts.
            run_complexity: Compute complexity features.
            run_connectivity: Compute connectivity metrics.
            
        Returns:
            Dictionary with all results.
        """
        if run_qeeg:
            self.results["qeeg"] = self.qeeg.analyze_data()

        if run_bursts:
            self.results["bursts"] = self.burst.detect_alpha_bursts().to_dict(orient="records")

        if run_complexity:
            self.results["complexity"] = self.complexity.compute_complexity_all_channels().to_dict(orient="records")

        if run_connectivity:
            self.results["connectivity"] = self.connectivity.compute_connectivity_all_bands()

        return self.results

    def save_results(self, output_path: str) -> None:
        """Save results to JSON file."""
        dict_to_json(self.results, output_path)

    def get_summary(self) -> Dict:
        """Get a summary of all results."""
        summary = {}
        
        if "qeeg" in self.results:
            summary["qeeg"] = {
                "n_channels": self.results["qeeg"].get("n_channels", 0),
                "bands": list(self.results["qeeg"].get("absolute_power", {}).keys()),
            }
        
        if "bursts" in self.results:
            burst_df = self.results["bursts"]
            summary["bursts"] = {
                "total_bursts": sum(b.get("n_bursts", 0) for b in burst_df),
                "avg_burst_fraction": sum(b.get("burst_fraction", 0) for b in burst_df) / len(burst_df) if burst_df else 0,
            }
        
        if "complexity" in self.results:
            summary["complexity"] = {
                "n_channels": len(self.results["complexity"]),
                "features": ["sample_entropy", "approximate_entropy", "hurst_exponent", 
                            "fractal_dimension", "lempel_ziv_complexity", "dfa_alpha", 
                            "permutation_entropy"],
            }
        
        if "connectivity" in self.results:
            summary["connectivity"] = {
                "bands": list(self.results["connectivity"].keys()),
                "metrics": ["wpli", "coherence", "psi"],
            }
        
        return summary


def run_pipeline(
    file_path: str,
    output_path: Optional[str] = None,
    l_freq: float = 1.0,
    h_freq: float = 25.0,
    remove_powerline: bool = True,
) -> Dict:
    """
    Convenience function to run the full pipeline.
    
    Parameters:
        file_path: Path to EEG file.
        output_path: Optional path to save JSON results.
        l_freq: Low frequency for bandpass filter.
        h_freq: High frequency for bandpass filter.
        remove_powerline: Whether to remove powerline noise.
        
    Returns:
        Dictionary with all analysis results.
    """
    pipeline = CerebroPipeline()
    pipeline.load_data(file_path)
    pipeline.preprocess_data(l_freq=l_freq, h_freq=h_freq, remove_powerline=remove_powerline)
    results = pipeline.run_full_analysis()
    
    if output_path:
        pipeline.save_results(output_path)
    
    return results
