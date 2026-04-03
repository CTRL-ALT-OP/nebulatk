import os
import sys


def use_local_nebulatk():
    """Ensure examples import the local repository package first."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    return repo_root


def example_path(*parts):
    """Build an absolute path from the examples directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *parts))
