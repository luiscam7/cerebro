"""
A collection of algorithms that can be used in the broad context of signal processing.
"""
import numpy as np
from scipy.integrate import simps


def calculate_total_area_under_curve(signal_curve: np.ndarray) -> float:
    """
    Calculate the total area under a curve using Simpson's rule.

    :param signal_curve: An array of signal values (y-values of the curve).
    :return: The total area under the curve.
    """
    # Create an array for the x-axis (indices)
    x_axis = np.arange(len(signal_curve))

    # Calculate the area using Simpson's rule
    total_area = simps(signal_curve, x_axis)

    return total_area
