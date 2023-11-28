from typing import Callable
from functools import wraps
from .params import DEFAULT_FLOAT_PRECISION


def set_precision(decimals: int = DEFAULT_FLOAT_PRECISION):
    """Decorator to round the result of a function to a specified number of decimal places."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return round(result, decimals)

        return wrapper

    return decorator
