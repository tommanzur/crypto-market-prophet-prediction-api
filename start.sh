#!/bin/bash
set -e
echo "Installing CmdStan..."
python -c "import cmdstanpy; cmdstanpy.install_cmdstan()"
echo "CmdStan ready. Starting server..."
cd src
uvicorn main:app --host 0.0.0.0 --port 8000
