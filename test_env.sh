#!/bin/bash
set -e

VENV_PYTHON="/opt/venv/bin/python3"

echo "=== Testing Python Environment ==="
if [ -f "$VENV_PYTHON" ]; then
    echo "Using Venv Python: $($VENV_PYTHON --version)"
    $VENV_PYTHON -c "import google.protobuf; print('✅ Protobuf is installed')"
else
    echo "❌ Error: Virtual environment not found at /opt/venv"
    exit 1
fi

echo -e "\n=== Testing Compilers ==="
g++ --version | head -n 1
cmake --version | head -n 1
cargo --version
mdbook --version

echo -e "\n✅ Environment check complete."
echo -e "\n✅ All basic tests passed! The environment is ready."
echo "To test grSim UI, run 'grSim' in the terminal."
echo "(If you get a display error, ensure you run 'xhost +local:docker' on your host machine before starting the container)"
