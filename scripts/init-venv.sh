#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR/.."

echo "Initialising virtual environment..."
python3.12 -m venv .venv
source .venv/bin/activate

echo "Venv initialised. Installing modules..."
tmpfile=$(mktemp)
cat {slackbot,worker,.}/requirements.txt > $tmpfile
pip install -r $tmpfile
rm $tmpfile

echo "Setup complete! Run scripts/dev.sh to start the development server!"