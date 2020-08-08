"""
Additional layer between LXD API and client.
Client supplemented by some useful functions.
Such as downloading image, wrappers above container states, etc.
"""

from .client import LXDClient

__all__ = [
    'LXDClient'
]
