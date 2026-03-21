"""
Ensure the generated *_pb2.py files in this directory can resolve their
bare sibling imports (e.g. `import ssl_vision_detection_pb2`).

protoc-generated Python files use bare module names instead of relative
imports, so the package directory must be on sys.path.
"""
import os, sys

_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)
