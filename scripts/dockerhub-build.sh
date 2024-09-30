#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR/.."

(cd slackbot && docker build --platform linux/amd64 -t tantosec/slashcat:slackbot .) || exit 1
(cd worker && docker build --platform linux/amd64 --build-arg WORKER_BASE=dizcza/docker-hashcat:intel-cpu -t tantosec/slashcat:worker .)

docker push tantosec/slashcat:slackbot
docker push tantosec/slashcat:worker