#!/bin/bash
# Author: Dot(anty2bot)
# Date: 2024-12-14
# Description: This is a Shell script for Multi V2ray Start/Stop

readonly DOCKER_IMAGE="docker.unsee.tech/v2fly/v2fly-core:v5.16.1"
readonly DOCKER_IMAGE_SHA256="sha256:d1c717b3cc8c7602fdb89a886d0c7fc0cf8c1d973501101d5f5e86f1ec6dcccf"
readonly V2RAY_CONFIG_FILE="/etc/v2ray/config.json"

setup_image() {
  if docker inspect "$DOCKER_IMAGE" > /dev/null 2>&1; then
    return
  fi

  echo "$DOCKER_IMAGE is not downloaded. Trying to pull the image..."
  for ((i=1; i<=5; i++)); do
    docker pull "$DOCKER_IMAGE"
    if docker inspect "$DOCKER_IMAGE" > /dev/null 2>&1; then
      break;
    fi
    echo "Download failed. Retrying in 3 seconds... ($i/5)"
    sleep 3
  done
}

setup_container() {
  if [ "$#" -lt "3" ]; then
    echo "Usage: setup_container [name] [port] [FLAG]"
    exit 1
  fi

  readonly local NAME="$1"
  readonly local PORT="$2"
  readonly local FLAG="$3"

  readonly local CONTAINER_NAME="v2ray-$NAME"
  readonly local CONTAINER_HTTP_PORT="$PORT"
  readonly local CONTAINER_SOCK_PORT="$(($PORT + 1))"

  docker container stop "$CONTAINER_NAME"
  docker container rm "$CONTAINER_NAME"
  if [ "$FLAG" == "off" ]; then
    echo "$CONTAINER_NAME: turn off"
    exit 0
  fi

  mv /tmp/config.json $V2RAY_CONFIG_FILE
  if ! [ -f "$V2RAY_CONFIG_FILE" ]; then
    echo "$V2RAY_CONFIG_FILE is not found"
    exit 1
  fi

  if ! [ "$(docker inspect --format '{{.Id}}' $DOCKER_IMAGE)" == "$DOCKER_IMAGE_SHA256" ]; then
    echo "$DOCKER_IMAGE is not valid"
    exit 1
  fi

  docker run -d \
    --name "$CONTAINER_NAME" \
    -v $V2RAY_CONFIG_FILE:$V2RAY_CONFIG_FILE \
    -p $CONTAINER_HTTP_PORT:$CONTAINER_HTTP_PORT \
    -p $CONTAINER_SOCK_PORT:$CONTAINER_SOCK_PORT \
    $DOCKER_IMAGE \
    run -c $V2RAY_CONFIG_FILE

  rm $V2RAY_CONFIG_FILE
}

setup_image
setup_container "$@"
