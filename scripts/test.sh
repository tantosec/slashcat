#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR/.."

source ./.venv/bin/activate

export PYTHONUNBUFFERED=true

if [[ $# -eq 0 ]]; then
    targets="slackbot worker"
else
    case "$1" in
        slackbot) targets=slackbot;;
        worker) targets=worker;;
        *)
            echo "Usage: $0 <slackbot|worker>";
            exit 1;;
    esac
fi

if [[ $# -gt 1 ]]; then
    if [[ "$1" = all ]]; then
        echo "Cannot use additional arguments with 'all'"
        exit 1
    fi

    (
        cd "$targets/src" && \
        python3 -m unittest "${@:2}"
    )
else
    runtests() {
        echo "======================================================================"
        echo "Running tests for $1"
        (
            cd "$1/src" && \
            if [[ $# -gt 1 ]]; then
                coverage run --source=. -m unittest "${@:2}";
            else
                coverage run --source=. -m unittest discover -s tests;
            fi && \
            echo && \
            echo Coverage: && \
            coverage report
        )
        retval=$?
        echo "======================================================================"
        return $retval
    }

    gencov() {
        (
            cd "$1/src" && \
            coverage html >/dev/null
        )
        echo "For coverage details for $1, visit $(pwd)/$1/src/htmlcov/index.html"
    }

    successful=0
    for t in $targets; do
        if runtests "$t"; then
            gencov "$t";
            successful=$((successful + 1))
        fi
    done

    numtargets=$(wc -w <<< "$targets")
    if [[ "$successful" -eq "$numtargets" ]]; then
        echo -e '\033[0;32m***********************'
        echo -e '  All tests passed :D'
        echo -e '***********************\033[0;0m'
        exit 0
    else
        echo -e '\033[0;31m*********************'
        echo -e '   TESTS FAILED D:'
        echo -e '*********************\033[0;0m'
        exit 1
    fi
fi