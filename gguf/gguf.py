import importlib
import sys
from pathlib import Path

# Insert the path to the GGUF package directory
gguf_package_dir = Path(__file__).parent.parent / 'gguf'
sys.path.insert(0, str(gguf_package_dir))

# Compatibility for people trying to import gguf/gguf.py directly instead of as a package.
importlib.invalidate_caches()

import gguf  # noqa: E402
importlib.reload(gguf)

from gguf import GGUFReader, GGUFValueType  # noqa: E402
