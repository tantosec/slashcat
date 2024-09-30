#!/bin/bash

if [[ "$1" != create ]] && [[ "$1" != list ]] && [[ "$1" != merge ]] && [[ "$1" != migrate ]] && [[ "$1" != rollback ]]; then
    pw_migrate --help
    exit 1
fi

(
    cd slackbot/src && \
    pw_migrate "$1" --directory migrations --database sqlite:///../../data/db/sqlite.db "${@:2}"
)
