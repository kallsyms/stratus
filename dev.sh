#!/bin/sh
export COMPOSE_FILE=docker-compose.dev.yaml
docker-compose up --no-start && docker-compose start
docker-compose exec wx_explore chmod -R 777 /opt/wx_explore/wx_explore/common/seed.py
docker-compose exec wx_explore /opt/wx_explore/wx_explore/common/seed.py
docker-compose exec wx_explore /bin/bash
