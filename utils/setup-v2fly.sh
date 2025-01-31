#!/bin/bash
# Author: Dot(anty2bot)
# Date: 2025-01-11
# Description: This is a Shell script for Multi V2Fly Start/Stop

readonly SCRIPT_PATH=$(dirname "$0")
readonly V2FLY_IMAGE="$(cat $SCRIPT_PATH/v2fly.sha256 | awk '{print $1}')"
readonly V2FLY_IMAGE_ID="$(cat $SCRIPT_PATH/v2fly.sha256 | awk '{print $2}')"

readonly DOCKER_IMAGE="${V2FLY_IMAGE_NAME:-v2fly/v2fly-core:v5.16.1}"
readonly DOCKER_IMAGE_ID="${V2FLY_IMAGE_ID:-sha256:d1c717b3cc8c7602fdb89a886d0c7fc0cf8c1d973501101d5f5e86f1ec6dcccf}"
readonly V2FLY_CONFIG_FILE="/etc/v2fly/config.json"

setup_image() {
  if docker inspect "$DOCKER_IMAGE" > /dev/null 2>&1; then
    return
  fi

  if [ -f /tmp/v2fly.tar ]; then
    docker load < /tmp/v2fly.tar
  fi

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
  if [ "$#" -lt "4" ]; then
    echo "Usage: setup_container [name] [port] [FLAG] [FILE]"
    return
  fi

  readonly local NAME="$1"
  readonly local PORT="$2"
  readonly local FLAG="$3"
  readonly local TEMP_V2FLY_CONFIG_FILE="$4"

  readonly local CONTAINER_NAME="v2fly-$NAME"
  readonly local CONTAINER_HTTP_PORT="$PORT"
  readonly local CONTAINER_SOCK_PORT="$(($PORT + 1))"

  docker container stop "$CONTAINER_NAME"
  docker container rm "$CONTAINER_NAME"
  if [ "$FLAG" == "off" ]; then
    echo "$CONTAINER_NAME: turn off"
    exit 0
  fi

  if ! [ -d "$(dirname $V2FLY_CONFIG_FILE)" ]; then
    mkdir -p "$(dirname $V2FLY_CONFIG_FILE)"
  fi

  mv $TEMP_V2FLY_CONFIG_FILE $V2FLY_CONFIG_FILE
  if ! [ -f "$V2FLY_CONFIG_FILE" ]; then
    echo "$V2FLY_CONFIG_FILE is not found"
    exit 1
  fi

  if ! [ "$(docker inspect --format '{{.Id}}' $DOCKER_IMAGE)" == "$DOCKER_IMAGE_ID" ]; then
    echo "$DOCKER_IMAGE is not valid"
    exit 1
  fi

  docker run -d \
    --name "$CONTAINER_NAME" \
    -v $V2FLY_CONFIG_FILE:$V2FLY_CONFIG_FILE \
    -p $CONTAINER_HTTP_PORT:$CONTAINER_HTTP_PORT \
    -p $CONTAINER_SOCK_PORT:$CONTAINER_SOCK_PORT \
    $DOCKER_IMAGE \
    run -c $V2FLY_CONFIG_FILE

  rm $V2FLY_CONFIG_FILE
}

setup_image
setup_container "$@"
