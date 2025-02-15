#!/bin/sh
export COMPOSE_FILE=docker-compose.dev.yaml
#docker compose build
docker compose up -d
