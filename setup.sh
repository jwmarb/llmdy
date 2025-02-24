#!/bin/bash
VENV=".venv"

if [ ! -d "$VENV" ]; then
  echo "Setting up virtual environment..."
  python3 -m venv "$VENV"
  echo "Created virtual environment at \"$VENV\""
fi

if [ -n "$VIRTUAL_ENV" ]; then
  source "$VENV/bin/activate"
fi

pip3 install -r requirements.txt \
&& maturin develop