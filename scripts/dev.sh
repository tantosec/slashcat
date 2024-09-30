#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR/.."

source .venv/bin/activate

export PYTHONUNBUFFERED=true
nodemon -e py -w slackbot/src -w worker/src -x \
    concurrently -n bot,worker \
    "bash -c 'cd slackbot && python3.12 src/main.py'" \
    "bash -c 'cd worker && python3.12 src/main.py'"