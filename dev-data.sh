#!/bin/sh
export COMPOSE_FILE=docker-compose.dev.yaml
docker-compose exec wx_explore /opt/wx_explore/wx_explore/ingest/sources/gfs.py --offset 1
docker-compose exec wx_explore /opt/wx_explore/wx_explore/ingest/sources/gfs.py --offset 2
docker-compose exec wx_explore /opt/wx_explore/wx_explore/ingest/sources/gfs.py --offset 3
docker-compose exec wx_explore /opt/wx_explore/wx_explore/ingest/worker.py
