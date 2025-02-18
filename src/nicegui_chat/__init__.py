"""Chat with AI"""

from importlib.metadata import metadata

import fire

from .chat import chat, distance, send

_package_metadata = metadata(str(__package__))
__version__ = _package_metadata["Version"]
__author__ = _package_metadata.get("Author-email", "")

__all__ = ["__author__", "__version__", "chat", "distance", "send"]


def main() -> None:
    """スクリプト実行"""
    fire.Fire(chat)
