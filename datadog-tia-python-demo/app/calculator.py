"""
Simple calculator module for demo purposes.
"""
from typing import Union

Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """Return the sum of two numbers."""
    print("Adding numbers:", a, "+", b)
    return a + b


def subtract(a: Number, b: Number) -> Number:
    """Return the difference of two numbers (a - b)."""
    
    return a - b
