#!/bin/bash
app="jij-api-service"
docker build -t ${app} .
docker run -d -p 56733:80 \
  -e DATABASE_URL="postgresql:///testdb" \
  --name=${app} \
  -v $PWD:/app ${app}

