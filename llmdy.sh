#!/bin/bash

export PYTHONPATH="$(pwd)/llmdy"

python3 -m llmdy "$@"