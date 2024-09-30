#!/bin/bash

docker build --platform linux/amd64 --build-arg WORKER_BASE=dizcza/docker-hashcat:intel-cpu -t tantosec/crackbox-testing:intel-cpu .
docker push tantosec/crackbox-testing:intel-cpu
