#!/bin/bash

# Ensure the directories exist
mkdir -p "/home/borsheng/searxng/config/" "/home/borsheng/searxng/data/"

# Docker command to run SearXNG
# Ensure you have removed any existing containers named 'searxng' if you encounter conflicts.
# You might need to run 'docker stop searxng' and 'docker rm searxng' manually before running this script if a container with that name already exists.
docker run --name searxng -d \
 -p 8888:8080 \
 -v "/home/borsheng/searxng/config/:/etc/searxng/" \
 -v "/home/borsheng/searxng/data/:/var/cache/searxng/" \
 docker.io/searxng/searxng:latest

echo "SearXNG container should now be running."
echo "Access it at http://localhost:8888"

