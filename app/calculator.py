"""
Simple calculator module for demo purposes.
"""
from typing import Union

Number = Union[int, float]


def add(a: Number, b: Number) -> Number:
    """Return the sum of two numbers."""
    c = a + b
    return c


def subtract(a: Number, b: Number) -> Number:
    """Return the difference of two numbers (a - b)."""
    c =  a - b

    return c


def multiply(a: Number, b: Number) -> Number:
    """Return the product of two numbers."""
    # m = a * b
    return a * b


def divide(a: Number, b: Number) -> Number:
    """Return the quotient of two numbers (a / b)."""
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b


def power(a: Number, b: Number) -> Number:
    """Return a raised to the power of b."""
    p = a ** b
    return p
