"""Alpha burst detection using neurodsp."""

import pandas as pd
import numpy as np
from typing import Dict, List
from cerebro.qeeg import QeegAnalysis
from cerebro.utils.params import CHANNELS_10_20, ALPHA_BAND
from neurodsp import burst


class BurstAnalysis(QeegAnalysis):
    """Detect alpha bursts across EEG channels using neurodsp."""

    def __init__(self):
        super().__init__()
        self.burst_results = None
        self.data = None

    def set_raw(self, raw):
        """Set raw EEG data directly."""
        self.data = raw

    def detect_alpha_bursts(
        self,
        threshold_2ndDeriv: float = 2.0,
        min_cycle_above_thresh: float = 0.01,
    ) -> pd.DataFrame:
        """
        Detect alpha bursts across all 19 channels.

        Parameters:
        threshold_2ndDeriv: Threshold for 2nd derivative burst detection.
            Lower = more sensitive, Higher = less sensitive. Default 2.0.
        min_cycle_above_thresh: Minimum fraction of cycle above threshold. Default 0.01.

        Returns:
        DataFrame with burst statistics per channel.
        """
        if self.data is None:
            raise ValueError("No data loaded. Run load_data() first.")

        # Get sampling frequency
        sf = self.data.info["sfreq"]
        
        # Get data as numpy array
        eeg_data = self.data.get_data(picks="eeg")
        
        results = []

        for idx, channel in enumerate(CHANNELS_10_20):
            signal = eeg_data[idx]
            
            # Compute burst detection using dual threshold gradient
            try:
                bursts = burst.compute_bursts_dual_threshold(
                    signal,
                    sf,
                    f_range=ALPHA_BAND,
                    threshold_2ndDeriv=threshold_2ndDeriv,
                    min_cycle_above_thresh=min_cycle_above_thresh,
                )
                
                n_bursts = len(bursts["burst_inds"])
                burst_fraction = bursts["burst_fraction"]
                n_cycles = bursts["n_cycles"]
                
                results.append({
                    "channel": channel,
                    "n_bursts": n_bursts,
                    "burst_fraction": burst_fraction,
                    "n_cycles": n_cycles,
                    "alpha_power_ratio": burst_fraction,
                })
                
            except Exception as e:
                results.append({
                    "channel": channel,
                    "n_bursts": 0,
                    "burst_fraction": 0.0,
                    "n_cycles": 0,
                    "alpha_power_ratio": 0.0,
                })

        self.burst_results = pd.DataFrame(results)
        
        # Calculate statistics
        self.analysis["alpha_bursts"] = self.burst_results.to_dict(orient="records")
        
        return self.burst_results

    def analyze_data(self) -> Dict:
        """Override to include burst detection."""
        super().analyze_data()
        self.detect_alpha_bursts()
        return self.analysis
